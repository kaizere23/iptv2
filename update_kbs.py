import asyncio
import sys
from playwright.async_api import async_playwright

TARGET_WEB = "https://www.bosstv.top/kor/kbs-world"
M3U_FILE = "kbs_world.m3u8"

async def main():
    captured_urls = []
    print("Memulakan pelanggan Playwright...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        async def handle_response(response):
            url = response.url
            if ".m3u8" in url:
                print(f"[SNIFFER DETECTED]: {url}")
                captured_urls.append(url)

        page.on("response", handle_response)

        try:
            print(f"Membuka URL sasaran: {TARGET_WEB}")
            await page.goto(TARGET_WEB, wait_until="domcontentloaded", timeout=45000)
            print("Menunggu pemain video dimuatkan...")
            await page.wait_for_timeout(10000)
        except Exception as e:
            print(f"Amaran semasa melayari laman: {e}")

        await browser.close()

    # Tentukan pautan akhir
    if captured_urls:
        final_stream_url = captured_urls[-1]
        print(f"Berjaya tangkap URL stream: {final_stream_url}")
    else:
        print("Amaran: Tiada pautan m3u8 dikesan oleh sniffer, menggunakan fallback.")
        final_stream_url = "https://www.bosstv.top/hls/kbs-world.m3u8"

    # Penulisan fail M3U
    m3u_content = f"""#EXTM3U
#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)
#EXTVLCOPT:http-referrer=https://www.bosstv.top/
{final_stream_url}
"""

    try:
        with open(M3U_FILE, "w", encoding="utf-8") as f:
            f.write(m3u_content)
        print(f"Fail {M3U_FILE} berjaya ditulis.")
    except Exception as e:
        print(f"Ralat semasa menulis fail M3U: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
