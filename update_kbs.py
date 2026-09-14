import asyncio
from playwright.async_api import async_playwright

TARGET_WEB = "https://www.bosstv.top/kor/kbs-world"
M3U_FILE = "kbs_world.m3u"

async def main():
    captured_urls = []

    async with async_playwright() as p:
        # Melancarkan browser headless dengan tetapan pelayar desktop sebenar
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()

        # FUNGSI SNIFFER: Dengar semua Network Responses
        async def handle_response(response):
            url = response.url
            # Tapis URL yang mempunyai .m3u8 atau pattern stream
            if ".m3u8" in url:
                print(f"[SNIFFER DETECTED]: {url}")
                captured_urls.append(url)

        page.on("response", handle_response)

        try:
            print("Membuka laman web BossTV & memulakan Sniffer...")
            await page.goto(TARGET_WEB, wait_until="domcontentloaded", timeout=40000)
            
            # Simulasi klik paut/play jika video perlukan interaksi pengguna
            await page.wait_for_timeout(3000)
            try:
                await page.click("video", timeout=3000)
            except Exception:
                pass

            # Beri masa 7 saat untuk sniffer tangkap manifest / segment playlist
            await page.wait_for_timeout(7000)

        except Exception as e:
            print(f"Ralat semasa sniffing: {e}")

        await browser.close()

    # Pilih URL m3u8 yang paling spesifik (keutamaan pada URL yang bertoken)
    final_stream_url = None
    if captured_urls:
        # Ambil URL terakhir yang dikesan (biasanya chunklist/playlist sebenar dengan token)
        final_stream_url = captured_urls[-1]
    else:
        print("Sniffer tidak jumpa URL dinamik, guna URL asas fallback...")
        final_stream_url = "https://www.bosstv.top/hls/kbs-world.m3u8"

    print(f"\n---> URL STREAM AKHIR: {final_stream_url}\n")

    # Format M3U khas untuk Jellyfin / OTT Navigator
    m3u_content = f"""#EXTM3U
#EXTINF:-1 group-title="Korea" tvg-id="KBSWorld.kr" tvg-name="KBS World" tvg-logo="https://i.imgur.com/v82M3U3.png",KBS World
#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)
#EXTVLCOPT:http-referrer=https://www.bosstv.top/
{final_stream_url}|Referer=https://www.bosstv.top/&User-Agent=Mozilla/5.0
"""

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"Fail {M3U_FILE} berjaya dikemas kini!")

if __name__ == "__main__":
    asyncio.run(main())
