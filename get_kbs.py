import re
from playwright.sync_api import sync_playwright


def get_live_m3u8():
    with sync_playwright() as p:
        # Buka headless browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        m3u8_url = None

        # Dengar (listen) semua rangkaian HTTP request yang keluar dari browser
        def handle_request(request):
            nonlocal m3u8_url
            if (
                "world-02" in request.url
                or "gscdn.kbs.co.kr" in request.url
            ) and ".m3u8" in request.url:
                if "Signature=" in request.url:
                    m3u8_url = request.url

        page.on("request", handle_request)

        print("Sedang memuatkan halaman KBS World...")
        page.goto(
            "https://world.kbs.co.kr/service/live_index.htm?lang=e",
            timeout=60000,
        )

        # Tunggu 10 saat untuk JavaScript selesai jana signed link
        page.wait_for_timeout(10000)

        browser.close()

        if m3u8_url:
            print(f"BERJAYA DAPAT SIGNED URL: {m3u8_url}")
            with open("kbs_world.m3u8", "w", encoding="utf-8") as f:
                f.write(
                    f"#EXTM3U\n#EXTINF:-1, KBS World Live\n{m3u8_url}\n"
                )
        else:
            print("Gagal menangkap URL M3U8 bernavigasi JS.")


if __name__ == "__main__":
    get_live_m3u8()
