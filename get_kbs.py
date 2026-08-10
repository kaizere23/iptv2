import sys
from playwright.sync_api import sync_playwright

PAGE_URL = "https://world.kbs.co.kr/service/live_index.htm?lang=e"


def fetch_signed_m3u8():
    with sync_playwright() as p:
        print("Luncurkan pelayar Chromium (Headless)...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        captured_url = None

        # Pintas & tangkap sebarang HTTP Request yang menuju ke gscdn/m3u8 berserta Signature
        def handle_request(request):
            nonlocal captured_url
            url = request.url
            if (
                "gscdn.kbs.co.kr" in url
                and ".m3u8" in url
                and "Signature=" in url
            ):
                captured_url = url
                print(f"\n[+] BERJAYA TANGKAP SIGNED URL:\n{captured_url}\n")

        page.on("request", handle_request)

        try:
            print("Melayari laman web KBS World...")
            page.goto(PAGE_URL, timeout=60000, wait_until="networkidle")

            # Tunggu 8 saat untuk memastikan JavaScript pemain video sempat berjalan
            page.wait_for_timeout(8000)

            # Jika masih belum dapat, cuba klik butang play jika wujud
            if not captured_url:
                print(
                    "Mencuba tekan butang play di halaman jika ada..."
                )
                play_button = page.query_selector(
                    "button.btn-play, .player-play, #playBtn"
                )
                if play_button:
                    play_button.click()
                    page.wait_for_timeout(5000)

        except Exception as e:
            print(f"Ralat semasa navigasi: {e}")

        browser.close()

        # Simpan pautan ke dalam fail kbs_world.m3u8
        if captured_url:
            m3u_content = f"#EXTM3U\n#EXTINF:-1, KBS World Live\n{captured_url}\n"
            with open("kbs_world.m3u8", "w", encoding="utf-8") as f:
                f.write(m3u_content)
            print("Fail kbs_world.m3u8 berjaya dikemaskini dengan Signed URL sah!")
        else:
            print(
                "[-] Gagal menangkap Signed URL dari trafik rangkaian."
            )
            sys.exit(1)


if __name__ == "__main__":
    fetch_signed_m3u8()
