import asyncio
import re
import sys
from playwright.async_api import async_playwright

async def get_kbs_stream():
    url = "https://vipotv.com/kbs-world"
    captured_urls = []

    async with async_playwright() as p:
        # Gunakan Chromium dengan User-Agent desktop biasa
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Pintas network request untuk cari .m3u8
        def handle_request(request):
            if ".m3u8" in request.url:
                print(f"[Jumpa M3U8]: {request.url}")
                captured_urls.append(request.url)

        page.on("request", handle_request)

        try:
            print(f"Mencari pautan stream KBS World di {url}...")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Tunggu 5 saat untuk player dimuatkan
            await page.wait_for_timeout(5000)

            # Cuba klik iframe/player jika video perlu di-play secara manual
            frames = page.frames
            for frame in frames:
                try:
                    await frame.click("video, .play-btn, #player", timeout=2000)
                except:
                    pass

            # Penantian tambahan untuk trafik M3U8 keluar
            await page.wait_for_timeout(7000)

        except Exception as e:
            print(f"[Warning] Ralat semasa memuatkan laman: {e}")
        finally:
            await browser.close()

    # Tapis URL m3u8 yang sah (abaikan iklan jika ada)
    valid_m3u8 = [u for u in captured_urls if "world" in u.lower() or "kbs" in u.lower() or "chunklist" in u.lower() or "playlist" in u.lower()]
    
    if valid_m3u8:
        return valid_m3u8[0]
    elif captured_urls:
        return captured_urls[0]
    else:
        return None

# Contoh pengendalian utama (main)
async def main():
    kbs_url = await get_kbs_stream()
    
    if not kbs_url:
        print("Ralat: Tiada pautan .m3u8 dikesan untuk KBS World.")
        # JANGAN sys.exit(1) jika anda mahu pipeline tetap berjaya (tidak menghantar exit code 1)
        # Boleh guna fallback URL di sini jika mahu:
        # kbs_url = "URL_BACKUP_KBS_ANDA"
        sys.exit(1)

    print(f"URL KBS World Terkini: {kbs_url}")

if __name__ == "__main__":
    asyncio.run(main())
