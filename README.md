# 🎬 Python Automation YouTube Shorts Clipper (Nope Code)

Pipeline otomasi cerdas berbasis Python untuk memproduksi video **YouTube Shorts vertikal (9:16)** secara mandiri:
1. **Scraping & Rotasi Topik Dinamis**: Mencari video wawancara/podcast tokoh teknologi dunia (*Sam Altman, Jensen Huang, Andrej Karpathy, Ilya Sutskever, dll.*) secara acak dan otomatis mencegah duplikasi video yang sudah pernah dibuat.
2. **Analisis AI (Google Gemini)**: Menganalisis transkrip panjang, menemukan momen viral (30-45 detik), membuat judul *curiosity gap*, deskripsi terstruktur, naskah, serta subtitle bahasa Indonesia.
3. **Dynamic Layout 9:16**: Background blurred + centered fit (tanpa memotong wajah tokoh di video podcast wide).
4. **Kinetic Subtitles (.ASS) & BGM**: Subtitle kinetik ber-outline tebal dan pencampuran musik latar via FFmpeg.
5. **High-Res Pro Poster Thumbnail (1080x1920)**: Pembuatan thumbnail portrait resolusi tinggi bergaya kreator pro menggunakan Pillow (clean frame tanpa subtitle + judul hook raksasa kuning + badge nama tokoh).
6. **Auto-Upload YouTube Data API v3**: Mengunggah video MP4 dan menyetel thumbnail kustom secara otomatis.

---

## 🚀 Fitur Unggulan

- 🧠 **AI-Powered Hook & Clipping**: Gemini secara otomatis memilih 30-45 detik momen paling berbobot.
- 🎯 **Algoritma Rotasi Dinamis**: Dilengkapi `used_videos.txt` dan generator topik acak sehingga setiap kali skrip dijalankan, tokoh dan videonya selalu berbeda.
- 🎨 **Pro Poster Thumbnail**: Menghasilkan thumbnail poster HD 1080x1920 dengan tipografi tebal, drop shadow, dan bingkai neon.
- 🧹 **Auto-Clean Folder**: Menjaga direktori kerja `final/` dan `making/` tetap bersih dan rapi.
- 📤 **One-Click YouTube Upload**: Otomasi OAuth 2.0 untuk upload Shorts dan pasang thumbnail.

---

## 📁 Struktur Direktori

```text
clipper-youtube/
├── assets/                  # Aset statis (misal: bgm.mp3 untuk musik latar)
├── final/                   # Output siap unggah (video .mp4, poster .jpg, detail .txt, latest_video.json)
├── making/                  # Ruang kerja sementara & riwayat used_videos.txt
├── main.py                  # Entry point CLI interaktif untuk menjalankan Process 1 & Process 2
├── process1.py              # Pipeline ekstraksi video, analisis Gemini, editing FFmpeg, & thumbnail pro
├── process2.py              # Pipeline autentikasi OAuth & upload video ke YouTube Data API
├── .env.example             # Template file environment variable
├── requirements.txt         # Daftar pustaka dependency Python
└── README.md
```

---

## 🛠️ Prasyarat

- **Python 3.9+** (Disarankan Python 3.10 atau 3.11)
- **Google Gemini API Key** (Dapatkan gratis di [Google AI Studio](https://aistudio.google.com/))
- **Google Cloud Console Project** (Aktifkan YouTube Data API v3 jika ingin fitur auto-upload)

---

## ⚙️ Panduan Instalasi & Penggunaan

### 1. Clone Repository
```bash
git clone https://github.com/nopecode96/python-automation-clipper-nope.git
cd python-automation-clipper-nope
```

### 2. Buat & Aktifkan Virtual Environment
```bash
# macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate

# Windows:
python -m venv .venv
.venv\Scripts\activate
```

### 3. Pasang Dependencies
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Environment Variable (`.env`)
Salin file `.env.example` menjadi `.env`, lalu masukkan API Key Anda:
```bash
cp .env.example .env
```

Buka file `.env` dan isi:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GROQ_API_KEY=your_optional_groq_key_here
```

### 5. (Opsional) Konfigurasi YouTube Data API untuk Auto-Upload
Jika ingin menggunakan modul upload otomatis ([process2.py](process2.py)):
1. Buat project di [Google Cloud Console](https://console.cloud.google.com/).
2. Aktifkan **YouTube Data API v3**.
3. Buat **OAuth 2.0 Client ID** (Application type: Desktop App).
4. Download file kredensial JSON dan simpan di root direktori dengan nama:
   ```text
   client_secrets.json
   ```
5. *(Opsional)* Letakkan musik latar santai di folder `assets/bgm.mp3` untuk efek background audio otomatis.

---

## 🎬 Menjalankan Skrip

### Opsi A: Jalankan Pipeline Penuh (Interaktif)
```bash
python main.py
```
- Anda dapat menekan **ENTER** untuk memilih topik trending acak secara otomatis, atau mengetikkan nama tokoh/topik tertentu.
- Di akhir pemrosesan, skrip akan menanyakan konfirmasi apakah ingin langsung mengunggah video ke YouTube beserta privasinya (*Private/Unlisted/Public*).

### Opsi B: Hanya Membuat Video & Thumbnail (Process 1)
```bash
python process1.py
```
Hasil akhir akan tersimpan di dalam folder `final/`:
- `final/short_<timestamp>.mp4` (Video vertikal 9:16 ber-subtitle kinetik)
- `final/short_<timestamp>_thumb.jpg` (Poster thumbnail pro 1080x1920)
- `final/short_<timestamp>_detail.txt` (Ringkasan judul, caption, naskah Indonesia & Inggris)
- `final/latest_video.json` (Data integrasi upload)

### Opsi C: Hanya Mengunggah Video Terbaru (Process 2)
```bash
python process2.py
```
Akan membaca file `final/latest_video.json` dan mengunggah video beserta thumbnail kustom ke channel YouTube Anda.

---

## 🔒 Catatan Keamanan
Jangan pernah mem-push file `.env`, `client_secrets.json`, atau `token.pickle` ke publik. File-file tersebut sudah dimasukkan ke dalam `.gitignore` bawaan.

---

## 👨‍💻 Kontributor
**Nope Code** - *AI, Coding & Technology Automation*
