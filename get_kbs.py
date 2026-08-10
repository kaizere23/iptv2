import json
import re
import requests

# URL rasmi siaran langsung KBS World
PAGE_URL = "https://world.kbs.co.kr/service/live_index.htm?lang=e"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://world.kbs.co.kr/",
}


def get_working_kbs_link():
    try:
        print("Sedang mengambil pautan M3U8 terkini dari KBS World...")
        res = requests.get(PAGE_URL, headers=headers, timeout=15)

        # Cari pautan gscdn m3u8 yang mempunyai parameter AWS Signed URL
        pattern = r"https://world\.gscdn\.kbs\.co\.kr/[^\s\"'\\]+\.m3u8\?[^\s\"'\\]+"
        match = re.search(pattern, res.text)

        if match:
            # Cuci sebarang watak escape (\) jika ada
            stream_url = match.group(0).replace("\\", "")
            print(f"Pautan Berjaya Ditemui: {stream_url}")
        else:
            print(
                "Pautan M3U8 dengan signature tidak ditemui dalam HTML, menggunakan fallback API..."
            )
            # Jika tiada dalam HTML, guna struktur M3U8 laluan selamat
            stream_url = "https://world.gscdn.kbs.co.kr/world-02/world-02_sd.m3u8"

        # Tulis kandungan ke fail M3U Playlist
        m3u_content = f"#EXTM3U\n#EXTINF:-1, KBS World Live\n{stream_url}\n"

        with open("kbs_world.m3u8", "w", encoding="utf-8") as f:
            f.write(m3u_content)

        print("Fail kbs_world.m3u8 berjaya dikemaskini!")

    except Exception as e:
        print(f"Ralat: {e}")


if __name__ == "__main__":
    get_working_kbs_link()
