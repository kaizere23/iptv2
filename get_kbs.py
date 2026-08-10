import requests

# Link M3U8 Master Akamai KBS World (Tidak Luput)
M3U8_URL = "https://kbsworld-ott.akamaized.net/hls/live/2002341/kbsworld/master.m3u8"

def generate_m3u8():
    try:
        print("Menjana fail playlist KBS World...")
        m3u_content = f"#EXTM3U\n#EXTINF:-1, KBS World Live\n{M3U8_URL}\n"
        
        with open("kbs_world.m3u8", "w", encoding="utf-8") as f:
            f.write(m3u_content)
            
        print("Fail kbs_world.m3u8 berjaya dicipta!")
    except Exception as e:
        print(f"Ralat: {e}")

if __name__ == "__main__":
    generate_m3u8()
