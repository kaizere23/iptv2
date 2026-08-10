import sys
from playwright.sync_api import sync_playwright

PAGE_URL = "https://world.kbs.co.kr/service/live_index.htm?lang=e"


def fetch_signed_m3u8():
    with sync_playwright() as p:
        print("Luncurkan pelayar Chromium dengan pintasan bot-detection...")

        # Gunakan argumen pintar untuk elak dikesan sebagai bot
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 720},
        )

        page = context.new_page()

        # Matikan bendera webdriver supaya tidak dikesan sebagai headless bot
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        captured_url = None

        # Dengar trafik rangkaian (termasuk iframe)
        def handle_request(request):
            nonlocal captured_url
            url = request.url
            if ".m3u8" in url and (
                "gscdn.kbs.co.kr" in url
                or "world" in url
                or "Signature=" in url
            ):
                if not captured_url or "Signature=" in url:
                    captured_url = url
                    print(f"\n[+] BERJAYA TANGKAP M3U8 URL:\n{captured_url}\n")

        page.on("request", handle_request)

        try:
            print("Melayari laman web KBS World...")
            page.goto(PAGE_URL, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)

            # Cari dan klik sebarang elemen video / frame / play
            print("Memulakan siaran video di halaman...")
            page.mouse.click(640, 360)  # Klik tengah skrin/player

            # Cuba tekan spacebar atau enter untuk start player
            page.keyboard.press("Space")

            # Tunggu sehingga 12 saat untuk network request dijana
            page.wait_for_timeout(12000)

            # Jika masih belum tangkap, periksa iframe
            if not captured_url:
                print("Memeriksa fail M3U8 di dalam iframe...")
                for frame in page.frames:
                    try:
                        frame.evaluate(
                            "document.querySelectorAll('video').forEach(v => v.play())"
                        )
                    except Exception:
                        pass
                page.wait_for_timeout(5000)

        except Exception as e:
            print(f"Ralat semasa navigasi: {e}")

        browser.close()

        # Simpan ke fail jika berjaya
        if captured_url:
            m3u_content = f"#EXTM3U\n#EXTINF:-1, KBS World Live\n{captured_url}\n"
            with open("kbs_world.m3u8", "w", encoding="utf-8") as f:
                f.write(m3u_content)
            print("Fail kbs_world.m3u8 berjaya dikemaskini!")
        else:
            print("[-] Gagal menangkap Signed URL dari trafik rangkaian.")
            sys.exit(1)


if __name__ == "__main__":
    fetch_signed_m3u8()
