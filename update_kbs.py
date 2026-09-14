import re
import requests

TARGET_WEB = "https://www.bosstv.top/kor/kbs-world"
M3U_FILE = "playlist.m3u"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://www.bosstv.top/"
}

try:
    # 1. Dapatkan sumber HTML
    response = requests.get(TARGET_WEB, headers=headers, timeout=10)
    response.raise_for_status()
    
    # 2. Cari pautan m3u8 menggunakan Regex
    match = re.search(r'https?://[^\s"\']+\.m3u8[^\s"\']*', response.text)
    
    if match:
        stream_url = match.group(0)
        print(f"URL Dijumpai: {stream_url}")
        
        # 3. Formatkan entri M3U
        m3u_content = f"""#EXTM3U
#EXTINF:-1 group-title="Korea" tvg-id="KBSWorld.kr" tvg-name="KBS World" tvg-logo="https://i.imgur.com/v82M3U3.png",KBS World
{stream_url}|Referer=https://www.bosstv.top/
"""
        # 4. Tulis ke fail playlist.m3u
        with open(M3U_FILE, "w", encoding="utf-8") as f:
            f.write(m3u_content)
        print("Fail playlist.m3u berjaya dikemas kini!")
    else:
        print("Pautan .m3u8 tidak dijumpai dalam HTML.")

except Exception as e:
    print(f"Ralat berlaku: {e}")
