import sys
from process1 import run_process1
from process2 import run_process2

def main():
    print("==================================================")
    print("  🎬 YOUTUBE SHORTS AUTOMATION PIPELINE")
    print("  Channel: Nope Code")
    print("==================================================")
    
    topic = input("Masukkan topik / nama tokoh (Tekan ENTER untuk Acak Trending Otomatis): ").strip()
    if not topic:
        topic = None

    # 1. Menjalankan Process 1 (Scrape, Analisa Gemini, Potong 9:16, Subtitle Indo, BGM)
    video_info = run_process1(custom_query=topic)
    
    if not video_info:
        print("\n❌ Pipeline dihentikan karena Process 1 gagal.")
        sys.exit(1)

    print("\n--------------------------------------------------")
    print("Proses pembuatan video selesai!")
    print(f"Judul: {video_info['title']}")
    print(f"File : {video_info['video_path']}")
    print("--------------------------------------------------")
    
    # Konfirmasi sebelum upload (bisa langsung upload atau ditinjau)
    upload_confirm = input("\nIngin langsung upload ke YouTube? (y/n, default: y): ").strip().lower()
    if upload_confirm in ["", "y", "yes"]:
        status_choice = input("Pilih visibilitas (1. Private / 2. Public / 3. Unlisted) [Default: 1]: ").strip()
        status_map = {"1": "private", "2": "public", "3": "unlisted"}
        chosen_status = status_map.get(status_choice, "private")

        run_process2(privacy=chosen_status)
    else:
        print("💡 Video disimpan secara lokal. Jalankan 'python process2.py' kapan saja untuk mengunggahnya.")

if __name__ == "__main__":
    main()