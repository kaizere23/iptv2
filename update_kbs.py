import asyncio
import re
import sys
from playwright.async_api import async_playwright

TARGET_WEB = "https://www.bosstv.top/kor/kbs-world"
MASTER_M3U = "playlist.m3u"  # Tukar nama fail ini jika fail utama anda guna nama lain (cth: index.m3u)

async def main():
    captured_urls = []
    print("Mencari pautan stream KBS World yang baharu...")

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
                print(f"[Dikesan]: {url}")
                captured_urls.append(url)

        page.on("response", handle_response)

        try:
            await page.goto(TARGET_WEB, wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(10000)
        except Exception as e:
            print(f"Amaran semasa melayari laman: {e}")

        await browser.close()

    if not captured_urls:
        print("Ralat: Tiada pautan .m3u8 baharu dikesan.")
        sys.exit(1)

    new_stream_url = captured_urls[-1]
    print(f"Pautan stream aktif berjaya diperolehi: {new_stream_url}")

    # Baca fail M3U utama dan kemas kini baris selepas KBS World
    try:
        with open(MASTER_M3U, "r", encoding="utf-8") as f:
            content = f.read()

        # Gunakan Regular Expression untuk mencari blok KBS World dan menggantikan URL di bawahnya
        pattern = r'(#EXTINF:-1.*?tvg-id="KBSWorld\.kr".*?\n(?:#EXTVLCOPT:.*\n)*)(https?://[^\s]+)'
        
        if not re.search(pattern, content):
            print("Ralat: Tag KBSWorld.kr tidak dijumpai dalam fail M3U utama.")
            sys.exit(1)

        updated_content = re.sub(pattern, rf'\1{new_stream_url}', content)

        with open(MASTER_M3U, "w", encoding="utf-8") as f:
            f.write(updated_content)

        print(f"Berjaya menyuntik pautan baharu terus ke dalam {MASTER_M3U}")

    except Exception as e:
        print(f"Ralat mengemas kini fail M3U: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
