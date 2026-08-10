import sys
import re
import requests

# Laman Penstriman Rasmi KBS World
PAGE_URL = "https://world.kbs.co.kr/service/live_index.htm?lang=e"
API_URL_V2 = "https://world.kbs.co.kr/api/live_url_v2.json?channel_code=12"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://world.kbs.co.kr/",
    "Origin": "https://world.kbs.co.kr",
}


def fetch_kbs_stream():
    stream_url = None

    # STRATEGI 1: Panggil API V2
    try:
        print("Mencuba API V2 KBS World...")
        res = requests.get(API_URL_V2, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            stream_url = data.get("url") or data.get("stream_url")
    except Exception as e:
        print(f"Ralat API V2: {e}")

    # STRATEGI 2: Imbas terus halaman HTML/JS siaran langsung
    if not stream_url:
        try:
            print("API V2 tiada respon. Memulakan imbasan halaman web...")
            res = requests.get(PAGE_URL, headers=headers, timeout=10)
            if res.status_code == 200:
                # Cari pola URL gscdn berserta Signature
                pattern = r"https://world\.gscdn\.kbs\.co\.kr/[^\s\"'\\]+\.m3u8\?[^\s\"'\\]+"
                match = re.search(pattern, res.text)
                if match:
                    stream_url = match.group(0).replace("\\", "")
        except Exception as e:
            print(f"Ralat Imbasan Web: {e}")

    # TULIS KE FAIL M3U8 JIKA BERJAYA
    if stream_url:
        print(f"\n[+] BERJAYA DAPAT SIGNED URL:\n{stream_url}\n")
        m3u_content = f"#EXTM3U\n#EXTINF:-1, KBS World Live\n{stream_url}\n"
        
        with open("kbs_world.m3u8", "w", encoding="utf-8") as f:
            f.write(m3u_content)
            
        print("Fail kbs_world.m3u8 berjaya dikemaskini!")
        return

    print("[-] Gagal mengekstrak Signed URL dari semua punca.")
    sys.exit(1)


if __name__ == "__main__":
    fetch_kbs_stream()
