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


# ---------------------------------------------------------
# 1. SNIFFER UNTUK KBS WORLD
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# 2. SNIFFER UNTUK TV2 (FORCE 1080P)
# ---------------------------------------------------------
async def sniff_tv2_1080p():
    captured_urls = []
    print(f"Mencari pautan stream TV2 (1080p) di {TARGET_TV2}...")

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

    valid_urls = [u for u in captured_urls if "tv2" in u.lower() or "tenbyte" in u.lower() or "rtm" in u.lower()]
    if not valid_urls:
        return None

    raw_url = valid_urls[-1]

    # Paksa tukar parameter kualiti rendah kepada 1080p
    url_1080p = raw_url.replace("tv2_720p", "tv2_1080p") \
                        .replace("tv2_480p", "tv2_1080p") \
                        .replace("tv2_360p", "tv2_1080p") \
                        .replace("index_720p", "index_1080p")

    return url_1080p


# ---------------------------------------------------------
# 3. LOGIK UTAMA KEMAS KINI FAIL M3U
# ---------------------------------------------------------
async def main():
    new_kbs_url = await sniff_kbs_world()
    new_tv2_url = await sniff_tv2_1080p()

    try:
        with open(MASTER_M3U, "r", encoding="utf-8") as f:
            content = f.read()

        updated = False

        # --- UPDATE KBS WORLD ---
        if new_kbs_url:
            kbs_block_pattern = r'#EXTINF:-1.*?tvg-id="KBSWorld\.kr".*?\n(?:#EXTVLCOPT:.*\n)*https?://[^\s]+'
            new_kbs_block = (
                '#EXTINF:-1 group-title="Korea" tvg-id="KBSWorld.kr" tvg-name="KBS World" tvg-logo="https://upload.wikimedia.org/wikipedia/commons/e/e2/KBS_World_2023.svg",KBS World\n'
                '#EXTVLCOPT:http-referrer=https://vipotv.com/\n'
                f'{new_kbs_url}'
            )
            if re.search(r'tvg-id="KBSWorld\.kr"', content):
                content = re.sub(kbs_block_pattern, new_kbs_block, content, flags=re.DOTALL)
                print(f"[SUKSES] KBS World dikemas kini -> {new_kbs_url}")
                updated = True
        else:
            print("[AMARAN] Tiada URL baharu dikesan untuk KBS World. Pautan sedia ada dikekalkan.")

        # --- UPDATE TV2 1080P ---
        if new_tv2_url:
            tv2_block_pattern = r'#EXTINF:-1.*?tvg-id="TV2\.my".*?\n(?:#EXTVLCOPT:.*\n)*https?://[^\s]+'
            new_tv2_block = (
                '#EXTINF:-1 group-title="Malaysia" tvg-id="TV2.my" tvg-name="TV2" tvg-logo="https://upload.wikimedia.org/wikipedia/commons/2/29/TV2_logo_2021.svg",TV2 (1080p)\n'
                '#EXTVLCOPT:http-referrer=https://www.mana2.my/\n'
                '#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)\n'
                f'{new_tv2_url}'
            )
            if re.search(r'tvg-id="TV2\.my"', content):
                content = re.sub(tv2_block_pattern, new_tv2_block, content, flags=re.DOTALL)
                print(f"[SUKSES] TV2 1080p dikemas kini -> {new_tv2_url}")
                updated = True
        else:
            print("[AMARAN] Tiada URL baharu dikesan untuk TV2. Pautan sedia ada dikekalkan.")

        # --- SIMPAN FAIL ---
        if updated:
            with open(MASTER_M3U, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"\nBerjaya mengemas kini {MASTER_M3U}!")
        else:
            print("\nTiada peranti/sumber baharu ditemui. Fail M3U dikekalkan.")

    except Exception as e:
        print(f"Ralat semasa membaca/menulis fail M3U: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
