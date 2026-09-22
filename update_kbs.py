import asyncio
import re
import sys
from urllib.parse import urljoin
from playwright.async_api import async_playwright
import requests

TARGET_KBS = "https://vipotv.com/kbs-world"
TARGET_TV2 = "https://www.mana2.my/channel/tv2"
MASTER_M3U = "myplaylist latest.m3u"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

async def sniff_kbs_world():
    captured_urls = []
    print(f"Mencari pautan stream KBS World di {TARGET_KBS}...")

    async with async_playwright() as p:
        # Launch chromium dengan flag tambahan untuk elak bot detection
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        context = await browser.new_context(
            user_agent=HEADERS["User-Agent"],
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()

        # Tangkap sebarang respon HTTP yang mengandungi .m3u8
        async def handle_response(response):
            url = response.url
            if ".m3u8" in url and "blob:" not in url:
                print(f"[Dikesan KBS]: {url}")
                captured_urls.append(url)

        page.on("response", handle_response)

        try:
            # Buka laman web dan tunggu DOM sedia
            await page.goto(TARGET_KBS, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)

            # Cari dan klik pada video/iframe untuk pemicu (trigger) loading .m3u8
            for frame in page.frames:
                try:
                    await frame.click("video, .play-button, #player", timeout=2000)
                except Exception:
                    pass

            # Penantian ekstra untuk network traffic
            await page.wait_for_timeout(10000)

        except Exception as e:
            print(f"Amaran semasa melayari KBS World: {e}")

        await browser.close()

    # Tapis URL m3u8 yang relevan
    valid_urls = [u for u in captured_urls if "kbs" in u.lower() or "world" in u.lower() or "m3u8" in u.lower()]
    
    if valid_urls:
        return valid_urls[-1]
    elif captured_urls:
        return captured_urls[-1]
    
    return None

async def main():
    new_kbs_url = await sniff_kbs_world()

    # Logik Fallback: Jika gagal dapat URL baharu, jangan terus sys.exit(1)
    if not new_kbs_url:
        print("[AMARAN] Tiada pautan .m3u8 baharu dikesan untuk KBS World.")
        print("[INFO] Mempertahankan pautan sedia ada dalam M3U untuk mengelakkan kegagalan workflow.")
        # Kita keluar dengan exit code 0 supaya GitHub Actions tidak tandakan merah/error
        sys.exit(0)

    print(f"\n-> Pautan KBS World Terkini: {new_kbs_url}\n")

    # Buka & Kemas kini fail M3U
    try:
        with open(MASTER_M3U, "r", encoding="utf-8") as f:
            content = f.read()

        kbs_pattern = r'(#EXTINF:-1.*?tvg-id="KBSWorld\.kr".*?\n(?:#EXTVLCOPT:.*\n)*)(https?://[^\s]+)'
        if re.search(kbs_pattern, content):
            updated_content = re.sub(kbs_pattern, rf'\1{new_kbs_url}', content)
            with open(MASTER_M3U, "w", encoding="utf-8") as f:
                f.write(updated_content)
            print(f"Berjaya mengemaskini KBS World dalam {MASTER_M3U}!")
        else:
            print("Ralat: Tag KBSWorld.kr tidak dijumpai dalam M3U.")
            sys.exit(1)

    except Exception as e:
        print(f"Ralat mengemas kini fail M3U: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
