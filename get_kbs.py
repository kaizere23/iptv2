import re
import requests

# URL halaman penstriman tempat terletaknya pemain video/audio KBS
TARGET_URL = "https://world.kbs.co.kr/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_fresh_m3u8():
    try:
        print("Mengekstrak pautan dari KBS...")
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.raise_for_status()

        # Regex untuk mengecam pautan gscdn.kbs.co.kr yang mempunyai parameter Signed URL (Policy, Signature, Key-Pair-Id)
        pattern = r"https://world\.gscdn\.kbs\.co\.kr/[^\s\"']+\.m3u8\?[^\s\"']+"
        match = re.search(pattern, response.text)

        if match:
            fresh_url = match.group(0)
            print(f"URL Baharu Diperoleh: {fresh_url}")

            # Simpan ke fail playlist IPTV (M3U)
            m3u_content = f"#EXTM3U\n#EXTINF:-1, KBS World Live\n{fresh_url}\n"

            with open("kbs_world.m3u8", "w", encoding="utf-8") as f:
                f.write(m3u_content)

            print("Fail kbs_world.m3u8 berjaya dikemaskini!")
        else:
            print("Gagal menjumpai pautan M3U8 dalam HTML halaman.")

    except Exception as e:
        print(f"Ralat semasa mengambil data: {e}")


if __name__ == "__main__":
    fetch_fresh_m3u8()
