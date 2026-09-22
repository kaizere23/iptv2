import asyncio
import re
import sys
from playwright.async_api import async_playwright

TARGET_KBS = "https://vipotv.com/kbs-world"
TARGET_TV2 = "https://www.mana2.my/channel/tv2"
MASTER_M3U = "myplaylist latest.m3u"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

# 1. SNIFFER UNTUK KBS WORLD
async def sniff_kbs_world():
    captured_urls = []
    print(f"Mencari pautan stream KBS World di {TARGET_KBS}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(user_agent=HEADERS["User-Agent"], viewport={"width": 1280, "height": 720})
        page = await context.new_page()

        async def handle_response(response):
            url = response.url
            if ".m3u8" in url and "blob:" not in url:
                print(f"[Dikesan KBS]: {url}")
                captured_urls.append(url)

        page.on("response", handle_response)

        try:
            await page.goto(TARGET_KBS, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)

            for frame in page.frames:
                try:
                    await frame.click("video, .play-button, #player", timeout=2000)
                except Exception:
                    pass

            await page.wait_for_timeout(8000)
        except Exception as e:
            print(f"Amaran semasa melayari KBS World: {e}")

        await browser.close()

    valid_urls = [u for u in captured_urls if "kbs" in u.lower() or "world" in u.lower() or "m3u8" in u.lower()]
    return valid_urls[-1] if valid_urls else (captured_urls[-1] if captured_urls else None)


# 2. SNIFFER UNTUK TV2 (MANA2.MY)
async def sniff_tv2():
    captured_urls = []
    print(f"Mencari pautan stream TV2 di {TARGET_TV2}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(user_agent=HEADERS["User-Agent"], viewport={"width": 1280, "height": 720})
        page = await context.new_page()

        async def handle_response(response):
            url = response.url
            if ".m3u8" in url and "blob:" not in url:
                print(f"[Dikesan TV2]: {url}")
                captured_urls.append(url)

        page.on("response", handle_response)

        try:
            await page.goto(TARGET_TV2, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)

            for frame in page.frames:
                try:
                    await frame.click("video, .vjs-big-play-button, #player", timeout=2000)
                except Exception:
                    pass

            await page.wait_for_timeout(8000)
        except Exception as e:
            print(f"Amaran semasa melayari TV2: {e}")

        await browser.close()

    valid_urls = [u for u in captured_urls if "tv2" in u.lower() or "tenbyte" in u.lower() or "m3u8" in u.lower()]
    return valid_urls[-1] if valid_urls else (captured_urls[-1] if captured_urls else None)


# 3. LOGIK UTAMA UNTUK SUNTIK KEDUA-DUA URL KE M3U
async def main():
    new_kbs_url = await sniff_kbs_world()
    new_tv2_url = await sniff_tv2()

    try:
        with open(MASTER_M3U, "r", encoding="utf-8") as f:
            content = f.read()

        updated = False

        # Kemas kini KBS World jika jumpa URL baharu
        if new_kbs_url:
            kbs_pattern = r'(#EXTINF:-1.*?tvg-id="KBSWorld\.kr".*?\n(?:#EXTVLCOPT:.*\n)*)(https?://[^\s]+)'
            if re.search(kbs_pattern, content):
                content = re.sub(kbs_pattern, rf'\1{new_kbs_url}', content)
                print(f"[SUKSES] KBS World dikemas kini -> {new_kbs_url}")
                updated = True
        else:
            print("[AMARAN] Tiada URL baharu dikesan untuk KBS World. Pautan sedia ada dikekalkan.")

        # Kemas kini TV2 jika jumpa URL baharu
        if new_tv2_url:
            tv2_pattern = r'(#EXTINF:-1.*?tvg-id="TV2\.my".*?\n(?:#EXTVLCOPT:.*\n)*)(https?://[^\s]+)'
            if re.search(tv2_pattern, content):
                content = re.sub(tv2_pattern, rf'\1{new_tv2_url}', content)
                print(f"[SUKSES] TV2 dikemas kini -> {new_tv2_url}")
                updated = True
        else:
            print("[AMARAN] Tiada URL baharu dikesan untuk TV2. Pautan sedia ada dikekalkan.")

        # Simpan fail jika ada perubahan
        if updated:
            with open(MASTER_M3U, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"\nBerjaya mengemas kini {MASTER_M3U}!")
        else:
            print("\nTiada peranti/sumber baharu ditemui untuk kedua-dua saluran. Fail M3U dikekalkan.")

    except Exception as e:
        print(f"Ralat semasa membaca/menulis fail M3U: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
