import re
import requests

TARGET_WEB = "https://www.bosstv.top/kor/kbs-world"
M3U_FILE = "kbs_world.m3u"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.bosstv.top/",
    "Accept": "*/*"
}

try:
    session = requests.Session()
    response = session.get(TARGET_WEB, headers=headers, timeout=15)
    response.raise_for_status()
    html_text = response.text

    # Regex ini menangkap .m3u8 KESELURUHAN termasuk token (?token=xxx atau ?auth=xxx dsb.)
    match = re.search(r'(https?://[^\s"\'<>]+?\.m3u8(?:\?[^\s"\'<>]+)?)', html_text)

    if match:
        stream_url_with_token = match.group(1)
        print(f"URL + Token dijumpai: {stream_url_with_token}")
    else:
        # Pautan alternatif/fallback jika regex tidak jumpa token dinamik dalam HTML kasar
        print("Token dinamik tidak dijumpai dalam HTML biasa, guna struktur fallback...")
        stream_url_with_token = "https://www.bosstv.top/hls/kbs-world.m3u8"

    # Bina format M3U
    m3u_content = f"""#EXTM3U
#EXTINF:-1 group-title="Korea" tvg-id="KBSWorld.kr" tvg-name="KBS World" tvg-logo="https://i.imgur.com/v82M3U3.png",KBS World
#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)
#EXTVLCOPT:http-referrer=https://www.bosstv.top/
{stream_url_with_token}|Referer=https://www.bosstv.top/
"""

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"Berjaya kemaskini {M3U_FILE}")

except Exception as e:
    print(f"Ralat berlaku: {e}")
