import asyncio
import re
import sys
from urllib.parse import urljoin
from playwright.async_api import async_playwright
import requests

# Konfigurasi Sasaran Web & Fail M3U Utama
TARGET_KBS = "https://vipotv.com/kbs-world"
TARGET_TV2 = "https://www.mana2.my/channel/tv2"
MASTER_M3U = "myplaylist latest.m3u"  # Tukar nama fail jika berbeza

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


# =========================================================
# 1. FUNGSI SNIFFER M3U8 (PLAYWRIGHT)
# =========================================================
async def sniff_m3u8(target_url, channel_name):
    captured_urls = []
    print(f"Mencari pautan stream {channel_name} di {target_url}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        context = await browser.new_context(user_agent=HEADERS["User-Agent"])
        page = await context.new_page()

        async def handle_response(response):
            url = response.url
            if ".m3u8" in url:
                print(f"[Dikesan {channel_name}]: {url}")
                captured_urls.append(url)

        page.on("response", handle_response)

        try:
            await page.goto(
                target_url, wait_until="domcontentloaded", timeout=45000
            )
            await page.wait_for_timeout(10000)
        except Exception as e:
            print(f"Amaran semasa melayari {channel_name}: {e}")

        await browser.close()

    if captured_urls:
        return captured_urls[-1]
    return None


# =========================================================
# 2. HELPER: PENYELESAIAN MASTER PLAYLIST TENBYTE (JIKA TV2 ADALAH MASTER)
# =========================================================
def resolve_tv2_if_master(tv2_url):
    """Jika URL TV2 yang dikesan dari mana2.my adalah Master Playlist,

    fungsi ini akan menukarnya ke Direct Chunk/Media Playlist secara
    automatik.
    """
    if "playlist.m3u8" in tv2_url and "tenbytecdn" in tv2_url:
        print(
            "Pautan TV2 dikesan sebagai Master Playlist Tenbyte. Memproses ke"
            " Direct Stream..."
        )
        try:
            res = requests.get(tv2_url, headers=HEADERS, timeout=10)
            lines = res.text.splitlines()

            for i, line in enumerate(lines):
                if line.startswith("#EXT-X-STREAM-INF"):
                    sub_path = lines[i + 1].strip()
                    direct_url = urljoin(tv2_url, sub_path)
                    print(f"[TV2 Direct Resolved]: {direct_url}")
                    return direct_url

            return tv2_url.replace(
                "/playlist.m3u8", "/abr/tv2_1080p/chunks.m3u8"
            )
        except Exception as e:
            print(f"Ralat semasa resolve TV2 Master: {e}")
            return tv2_url
    return tv2_url


# =========================================================
# 3. UTAMA: JALANKAN PROSES & KEMAS KINI M3U
# =========================================================
async def main():
    # 1. Dapatkan URL M3U8 terkini untuk KBS World dan TV2 menerusi Playwright
    new_kbs_url = await sniff_m3u8(TARGET_KBS, "KBS World")
    raw_tv2_url = await sniff_m3u8(TARGET_TV2, "TV2")

    if not new_kbs_url:
        print("Ralat: Tiada pautan .m3u8 dikesan untuk KBS World.")
        sys.exit(1)

    if not raw_tv2_url:
        print("Ralat: Tiada pautan .m3u8 dikesan untuk TV2 dari mana2.my.")
        sys.exit(1)

    # 2. Laraskan pautan TV2 jika ia memerlukan penukaran Master -> Media Playlist
    new_tv2_url = resolve_tv2_if_master(raw_tv2_url)

    print(f"\n-> KBS World Stream: {new_kbs_url}")
    print(f"-> TV2 Stream: {new_tv2_url}\n")

    # 3. Baca fail M3U utama dan suntik URL baharu
    try:
        with open(MASTER_M3U, "r", encoding="utf-8") as f:
            content = f.read()

        # Update KBS World
        kbs_pattern = r'(#EXTINF:-1.*?tvg-id="KBSWorld\.kr".*?\n(?:#EXTVLCOPT:.*\n)*)(https?://[^\s]+)'
        if not re.search(kbs_pattern, content):
            print(
                "Ralat: Tag KBSWorld.kr tidak dijumpai dalam fail M3U"
                " utama."
            )
            sys.exit(1)
        content = re.sub(kbs_pattern, rf"\1{new_kbs_url}", content)

        # Update TV2
        tv2_pattern = r'(#EXTINF:-1.*?tvg-id="TV2\.my".*?\n(?:#EXTVLCOPT:.*\n)*)(https?://[^\s]+)'
        if not re.search(tv2_pattern, content):
            print("Ralat: Tag TV2.my tidak dijumpai dalam fail M3U utama.")
            sys.exit(1)
        content = re.sub(tv2_pattern, rf"\1{new_tv2_url}", content)

        # Simpan perubahan
        with open(MASTER_M3U, "w", encoding="utf-8") as f:
            f.write(content)

        print(
            f"Berjaya mengemaskini pautan KBS World dan TV2 dalam"
            f" {MASTER_M3U}!"
        )

    except Exception as e:
        print(f"Ralat mengemas kini fail M3U: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
