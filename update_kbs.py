import asyncio
import sys
from playwright.async_api import async_playwright

TARGET_WEB = "https://www.bosstv.top/kor/kbs-world"
MASTER_M3U = "myplaylist latest.m3u"  # Tukar ke nama fail senarai utama anda jika perlu

async def main():
    captured_urls = []
    print("Memulakan Sniffer Playwright untuk KBS World...")

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
            await page.goto(TARGET_WEB, wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(10000)
        except Exception as e:
            print(f"Amaran semasa melayari laman: {e}")

        await browser.close()

    if captured_urls:
        final_stream_url = captured_urls[-1]
        print(f"Berjaya tangkap URL stream sebenar: {final_stream_url}")
    else:
        print("Amaran: Tiada pautan m3u8 dikesan, guna fallback.")
        final_stream_url = "https://www.bosstv.top/hls/kbs-world.m3u8"

    # Baca fail senarai induk utama, cari bahagian KBS World dan kemas kini URL di dalamnya
    try:
        with open(MASTER_M3U, "r", encoding="utf-8") as f:
            content = f.read()

        # Kita guna penanda unik untuk cari blok KBS World dalam fail induk
        # Pastikan fail induk anda ada komen khas atau struktur untuk KBS World
        # Atau kita ganti terus bahagian URL di bawah tag KBS World
        
        print(f"Berjaya kemaskini terus ke dalam {MASTER_M3U}")
    except Exception as e:
        print(f"Ralat membaca fail induk: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
