import sys
import requests

# API Rasmi Penstriman KBS World Live (Channel Code 12 = KBS World)
API_URL = "https://world.kbs.co.kr/api/live_url.json?channel_code=12"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Referer": "https://world.kbs.co.kr/service/live_index.htm?lang=e",
    "Origin": "https://world.kbs.co.kr",
}


def fetch_kbs_stream():
    try:
        print("Meminta pautan M3U8 terus dari API KBS World...")
        response = requests.get(API_URL, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            # Mencari key URL dalam respons JSON
            stream_url = data.get("url") or data.get("stream_url") or data.get("live_url")

            # Jika API memulangkan struktur turutan/nested JSON
            if not stream_url and isinstance(data, dict):
                for key, val in data.items():
                    if isinstance(val, str) and "m3u8" in val:
                        stream_url = val
                        break

            if stream_url:
                print(f"\n[+] BERJAYA DAPAT SIGNED URL:\n{stream_url}\n")
                
                # Tulis terus ke fail kbs_world.m3u8
                m3u_content = f"#EXTM3U\n#EXTINF:-1, KBS World Live\n{stream_url}\n"
                with open("kbs_world.m3u8", "w", encoding="utf-8") as f:
                    f.write(m3u_content)
                
                print("Fail kbs_world.m3u8 berjaya dikemaskini!")
                return

        print(f"[-] API memulangkan status code: {response.status_code} atau tiada URL.")

    except Exception as e:
        print(f"Ralat panggila API: {e}")

    # Fallback jika API terhad: Bina pautan langsung dinamik
    sys.exit(1)


if __name__ == "__main__":
    fetch_kbs_stream()
