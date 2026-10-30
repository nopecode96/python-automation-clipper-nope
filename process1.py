import os
import sys
import json
import time
import random
import subprocess
import imageio_ffmpeg
import yt_dlp
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from google.genai import types

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY belum diset di .env!")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAKING_DIR = os.path.join(BASE_DIR, "making")
FINAL_DIR = os.path.join(BASE_DIR, "final")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

os.makedirs(MAKING_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

HISTORY_FILE = os.path.join(MAKING_DIR, "used_videos.txt")

TECH_VISIONARIES = [
    "Sam Altman",
    "Jensen Huang",
    "Andrej Karpathy",
    "Elon Musk",
    "Ilya Sutskever",
    "Demis Hassabis",
    "Mark Zuckerberg",
    "Dario Amodei",
    "Yann LeCun",
    "Satya Nadella",
    "Sundar Pichai",
    "Lex Fridman AI interview",
    "Dwarkesh Patel AI podcast"
]

TOPIC_ANGLES = [
    "AI future prediction interview",
    "AGI timeline coding talk",
    "AI agents replacing software engineers",
    "superintelligence warning interview",
    "robotics and humanoid AI talk",
    "vibe coding software engineering podcast",
    "deep learning breakthrough interview"
]

def get_used_video_ids():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def mark_video_as_used(video_id):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{video_id}\n")

def generate_trending_topic():
    """
    Menghasilkan query pencarian trending yang bervariasi menggunakan Gemini AI
    atau kombinasi acak tokoh + angle teknologi terkini.
    """
    selected_persona = random.choice(TECH_VISIONARIES)
    selected_angle = random.choice(TOPIC_ANGLES)
    try:
        candidate_models = ['gemini-3.8-flash', 'gemini-3.5-flash-lite', 'gemini-flash-latest']
        prompt = (
            f"Fokus pada tokoh: '{selected_persona}'. "
            f"Fokus pada tema: '{selected_angle}'. "
            "Buat 1 query pencarian YouTube singkat (dalam Bahasa Inggris) untuk mencari wawancara, podcast, atau keynote "
            "paling viral dan menarik dari tokoh ini. "
            "KEMBALIKAN HANYA 1 BARIS TEKS QUERY (3-6 kata, tanpa tanda kutip):"
        )
        for m in candidate_models:
            try:
                res = client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=1.0)
                )
                query = res.text.strip().replace('"', '').replace("'", "").split("\n")[0].strip()
                if query and len(query) > 5:
                    return query
            except Exception:
                continue
    except Exception:
        pass

    return f"{selected_persona} {selected_angle}"

    # Fallback kombinasi tokoh acak + sudut pandang acak
    tokoh = random.choice(TECH_VISIONARIES)
    angle = random.choice(TOPIC_ANGLES)
    return f"{tokoh} {angle}"

# -------------------------------------------------------------
# 1. CARI WAWANCARA TOKOH DUNIA DI YOUTUBE (NATIVE PYTHON)
# -------------------------------------------------------------
def search_viral_tech_interview(query=None):
    if not query:
        query = generate_trending_topic()

    print(f"\n[1/5] 🔍 Mencari wawancara viral tokoh dunia: '{query}'...")
    
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Cari 15 video teratas agar pilihan lebih kaya
            search_results = ydl.extract_info(f"ytsearch15:{query}", download=False)
            
            if not search_results or 'entries' not in search_results:
                print("⚠️ Tidak ada hasil video yang ditemukan dengan query ini, mencoba query cadangan...")
                backup_query = f"{random.choice(TECH_VISIONARIES)} AI interview podcast"
                search_results = ydl.extract_info(f"ytsearch15:{backup_query}", download=False)

            if not search_results or 'entries' not in search_results:
                print("⚠️ Gagal menemukan video.")
                return None, None

            candidates = []
            for entry in search_results['entries']:
                if not entry:
                    continue
                duration = entry.get('duration') or 0
                # Filter durasi: di atas 5 menit (300 detik)
                if duration > 300:
                    candidates.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'view_count': entry.get('view_count') or 0
                    })

            if not candidates:
                first_entry = search_results['entries'][0]
                candidates.append({
                    'id': first_entry.get('id'),
                    'title': first_entry.get('title'),
                    'view_count': first_entry.get('view_count') or 0
                })

            # Saring kandidat agar tidak memilih video yang sudah pernah dipakai
            used_ids = get_used_video_ids()
            fresh_candidates = [c for c in candidates if c['id'] not in used_ids]

            if not fresh_candidates:
                print("ℹ️ Semua video dari topik ini sudah pernah diproses, mencoba query tokoh lain...")
                for alt_tokoh in random.sample(TECH_VISIONARIES, min(4, len(TECH_VISIONARIES))):
                    alt_q = f"{alt_tokoh} {random.choice(TOPIC_ANGLES)}"
                    alt_res = ydl.extract_info(f"ytsearch10:{alt_q}", download=False)
                    if alt_res and 'entries' in alt_res:
                        for entry in alt_res['entries']:
                            if entry and entry.get('id') not in used_ids and (entry.get('duration') or 0) > 300:
                                fresh_candidates.append({
                                    'id': entry.get('id'),
                                    'title': entry.get('title'),
                                    'view_count': entry.get('view_count') or 0
                                })
                        if fresh_candidates:
                            break

            if fresh_candidates:
                # Urutkan berdasarkan views terbanyak, lalu pilih dari 3 teratas secara variatif
                fresh_candidates.sort(key=lambda x: x['view_count'], reverse=True)
                top_pool = fresh_candidates[:min(3, len(fresh_candidates))]
                top_video = random.choice(top_pool)
            else:
                top_video = random.choice(candidates)
            
            v_id = top_video['id']
            v_title = top_video['title']
            mark_video_as_used(v_id)

            print(f"      🎯 Ditemukan : {v_title}")
            print(f"      👁️ Views     : {top_video['view_count']:,} views")
            print(f"      🔗 Link      : https://www.youtube.com/watch?v={v_id}")
            return v_id, v_title
            
    except Exception as e:
        print(f"❌ Gagal mencari video via yt-dlp: {e}")
        return None, None

# -------------------------------------------------------------
# 2. AMBIL TRANSKRIP & DETEKSI TITIK VIRAL VIA GEMINI
# -------------------------------------------------------------
def get_transcript(video_id):
    try:
        # Dukungan youtube-transcript-api v1.2+
        if hasattr(YouTubeTranscriptApi, 'fetch'):
            yt_api = YouTubeTranscriptApi()
            transcript_obj = yt_api.fetch(video_id, languages=['en', 'en-US'])
            return transcript_obj.to_raw_data() if hasattr(transcript_obj, 'to_raw_data') else [
                {"text": s.text, "start": s.start, "duration": s.duration} for s in transcript_obj
            ]
        elif hasattr(YouTubeTranscriptApi, 'get_transcript'):
            return YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US'])
        else:
            yt_api = YouTubeTranscriptApi()
            transcript_obj = yt_api.fetch(video_id)
            return transcript_obj.to_raw_data()
    except Exception as e:
        print(f"⚠️ Gagal menarik transkrip: {e}")
        return None

def analyze_and_translate_clip(transcript_data, video_title):
    print("\n[2/5] 🧠 Gemini menganalisa momen viral, menyusun judul, naskah, & subtitle...")
    
    # Ambil sampel transkrip (sekitar 300 baris dialog pertama)
    sample_text = ""
    for item in transcript_data[:300]:
        m, s = divmod(int(item["start"]), 60)
        sample_text += f"[{m:02d}:{s:02d}] {item['text']}\n"

    # Prompt spesifik & kontekstual
    prompt = f"""
    Anda adalah Executive Content Strategist & Video Editor kelas dunia untuk channel YouTube Shorts "Nope Code" (fokus pada AI, Coding, dan Teknologi Masa Depan).

    TARGET VIDEO:
    Judul Asli: "{video_title}"
    Transkrip Wawancara (Bahasa Inggris):
    {sample_text}

    TUGAS UTAMA:
    1. ANALISIS VIRALITAS:
       - Pilih SATU segmen paling berbobot, berani, atau mengejutkan dengan durasi antara 30 hingga 45 detik.
       - Tentukan 'start_time' dan 'end_time' (dalam detik bilangan bulat / integer).
       - Pastikan segmen memiliki hook kuat di 3 detik pertama dan konklusi yang utuh (tidak terpotong di tengah kalimat).

    2. METADATA YOUTUBE & POSTER THUMBNAIL PRO:
       - 'title': Judul YouTube Shorts berbahasa Indonesia yang sangat memancing rasa penasaran (Curiosity Gap) tapi bukan clickbait murahan. Maksimal 70 karakter.
       - 'thumb_hook_title': Teks utama poster thumbnail yang sangat besar, berani, dan pendek (2-3 KATA DALAM HURUF BESAR / UPPERCASE, contoh: "VIBE CODING", "AGI 2026?!", "ERA BARU AI").
       - 'thumb_sub_hook': Teks penjelas pemancing klik di atas/bawah hook utama (1 kalimat pendek, contoh: "Beneran Bisa Rp 50 Juta?", "Coding Tradisional Tamat?").
       - 'image_prompt': Deskripsi visual untuk scene poster tokoh AI (close-up dramatis, cinematic lighting, neon cyan dan electric blue tech background).
       - 'caption': Deskripsi lengkap video berformat:
         * Hook / Pernyataan kontroversial tokoh (1 kalimat)
         * Rangkuman 2 poin wawasan penting
         * CTA: "Subscribe @NopeCode untuk insight AI & dev masa depan!"
         * 4-5 hashtag relevan (contoh: #AI #TechNews #Coding #NopeCode #Shorts)

    3. DOKUMENTASI NASKAH (SCRIPT):
       - 'script_en': Transkrip dialog asli bahasa Inggris pada segmen yang dipilih.
       - 'script_id': Terjemahan naskah dialog tersebut ke dalam Bahasa Indonesia yang santai, lugas, dan mudah dipahami.

    4. SUBTITLE KINETIK (.ASS COMPATIBLE):
       - Pecah naskah ke dalam array 'subtitles'.
       - Setiap elemen berisi:
         * 'start': detik mulai (relatif atau absolut)
         * 'end': detik selesai
         * 'text': 3-5 KATA SAJA DALAM HURUF BESAR (UPPERCASE) Bahasa Indonesia agar mudah dibaca cepat di layar HP vertikal.

    KEMBALIKAN HANYA FORMAT JSON VALID BERIKUT (TANPA MARKDOWN TAMBAHAN):
    {{
      "start_time": 120,
      "end_time": 155,
      "title": "Sam Altman: Jangan Belajar Koding Tradisional Lagi?!",
      "thumb_hook_title": "VIBE CODING",
      "thumb_sub_hook": "Beneran Bisa Rp 50 Juta?",
      "image_prompt": "Cinematic portrait of a tech visionary smiling confidently, neon cyan and yellow rim lighting, dark cyberpunk digital matrix background, 8k render",
      "script_en": "Text of the english transcript here...",
      "script_id": "Naskah terjemahan bahasa indonesia di sini...",
      "caption": "Pernyataan berani dari tokoh AI ini bakal ubah cara kerja kita.\\n\\nInsight Utama:\\n1. AI Agent akan menangani tugas repetitif.\\n2. Developer masa depan bertindak sebagai arsitek logika.\\n\\nSubscribe @NopeCode untuk insight harian!\\n\\n#AI #Technology #SamAltman #NopeCode #Shorts",
      "subtitles": [
        {{"start": 120.0, "end": 123.0, "text": "KITA SEDANG MEMASUKI"}},
        {{"start": 123.0, "end": 126.5, "text": "ERA BARU SOFTWARE"}}
      ]
    }}
    """
    
    # Coba model utama dengan fallback jika model tidak tersedia / kuota
    candidate_models = ['gemini-2.5-flash', 'gemini-3.1-flash-lite-preview', 'gemini-3.5-flash-lite', 'gemini-flash-latest']
    for model_name in candidate_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.6
                )
            )
            raw_text = response.text.strip() if response and response.text else ""
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            data = json.loads(raw_text.strip())
            # Validasi rentang waktu terhadap durasi transkrip aktual
            max_transcript_time = int(transcript_data[-1]["start"] + transcript_data[-1].get("duration", 10))
            if data.get("end_time", 0) > max_transcript_time or data.get("start_time", 0) >= max_transcript_time:
                safe_start = max(10, max_transcript_time - 45)
                safe_end = min(safe_start + 38, max_transcript_time)
                data["start_time"] = int(safe_start)
                data["end_time"] = int(safe_end)

            print(f"      📌 Judul Dipilih : {data.get('title')}")
            print(f"      ⏱️ Durasi Segmen : {data.get('start_time')}s -> {data.get('end_time')}s")
            return data
        except Exception:
            continue

    print(f"❌ Gagal memproses prompt Gemini: semua model kandidat gagal.")
    return None

# -------------------------------------------------------------
# 3. DOWNLOAD SEGMENT & KONVERSI KE VERTICAL 9:16 (BLURRED BG + CENTERED FIT)
# -------------------------------------------------------------
def download_cut_crop(video_id, start_sec, end_sec, output_path):
    print(f"\n[3/5] ✂️ Mengunduh dan mengonversi video detik {start_sec} s/d {end_sec} (Blurred Background + Centered Fit 9:16)...")
    url = f"https://www.youtube.com/watch?v={video_id}"
    temp_clip = os.path.join(MAKING_DIR, f"raw_{video_id}.mp4")

    if os.path.exists(temp_clip):
        try: os.remove(temp_clip)
        except Exception: pass

    cmd_dl = [
        sys.executable, "-m", "yt_dlp",
        "--ffmpeg-location", FFMPEG_EXE,
        "--extractor-args", "youtube:player_client=android,web",
        "--download-sections", f"*{start_sec}-{end_sec}",
        "-f", "b/bestvideo+bestaudio/best",
        "-o", temp_clip,
        url
    ]
    res_dl = subprocess.run(cmd_dl, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Jika gagal dengan download-sections, fallback download whole lalu potong via ffmpeg
    if res_dl.returncode != 0 or not os.path.exists(temp_clip) or os.path.getsize(temp_clip) == 0:
        print(f"⚠️ Mencoba format alternatif untuk mengunduh...")
        cmd_fallback = [
            sys.executable, "-m", "yt_dlp",
            "--ffmpeg-location", FFMPEG_EXE,
            "--extractor-args", "youtube:player_client=android,web",
            "--download-sections", f"*{start_sec}-{end_sec}",
            "-o", temp_clip,
            url
        ]
        subprocess.run(cmd_fallback, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not os.path.exists(temp_clip) or os.path.getsize(temp_clip) == 0:
        print(f"❌ Gagal mengunduh klip video dari YouTube.")
        return False

    # Layout Dinamis:
    # 1. Background: di-scale penuh vertical 1080x1920 (crop center) + efek boxblur=20:20
    # 2. Foreground: video asli di-scale fit lebar 1080px diletakkan di tengah (W-w)/2:(H-h)/2 tanpa memotong wajah tokoh
    filter_complex = (
        "[0:v]split=2[bg][fg];"
        "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:20[blurred];"
        "[fg]scale=1080:-1[foreground];"
        "[blurred][foreground]overlay=(W-w)/2:(H-h)/2[v]"
    )

    cmd_crop = [
        FFMPEG_EXE, "-y",
        "-i", temp_clip,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "fast",
        "-c:a", "aac",
        output_path
    ]
    subprocess.run(cmd_crop, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(temp_clip):
        try: os.remove(temp_clip)
        except Exception: pass

    return os.path.exists(output_path) and os.path.getsize(output_path) > 0

# -------------------------------------------------------------
# 4. BUAT SUBTITLE KINETIK BAHASA INDONESIA (.ASS)
# -------------------------------------------------------------
def create_ass_subtitle(subs_data, offset_start, output_ass):
    print("\n[4/5] 🎨 Menyusun file subtitle kinetik (.ass)...")
    def format_time(s):
        h, rem = divmod(s, 3600)
        m, sec = divmod(rem, 60)
        return f"{int(h):d}:{int(m):02d}:{sec:05.2f}"

    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,74,&H0000FFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,5,3,2,60,60,450,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for item in subs_data:
        # Relatifkan waktu terhadap detik awal pemotongan
        s = max(0.0, item["start"] - offset_start)
        e = max(s + 0.8, item["end"] - offset_start)
        text_clean = item["text"].strip().upper()
        lines.append(f"Dialogue: 0,{format_time(s)},{format_time(e)},Default,,0,0,0,,{text_clean}")

    with open(output_ass, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(lines))

# -------------------------------------------------------------
# 5. MIX BGM PELAN & HARDSUB SUBTITLE
# -------------------------------------------------------------
def render_final(cut_video, ass_file, final_output):
    print("\n[5/5] 🎬 Membakar subtitle & memadukan BGM via FFmpeg...")
    bgm_path = os.path.join(ASSETS_DIR, "bgm.mp3")
    escaped_ass = ass_file.replace(":", "\\:").replace("'", "\\'")

    if os.path.exists(bgm_path):
        # Suara tokoh 100%, BGM 12%
        filter_complex = (
            f"[0:v]ass='{escaped_ass}'[v];"
            f"[1:a]volume=0.12[bgm];"
            f"[0:a][bgm]amix=inputs=2:duration=first[a]"
        )
        cmd = [
            FFMPEG_EXE, "-y",
            "-i", cut_video,
            "-stream_loop", "-1", "-i", bgm_path,
            "-filter_complex", filter_complex,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            final_output
        ]
    else:
        # Tanpa BGM (hanya suara asli tokoh + subtitle)
        cmd = [
            FFMPEG_EXE, "-y",
            "-i", cut_video,
            "-vf", f"ass='{escaped_ass}'",
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "copy",
            final_output
        ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def clean_final_dir():
    """
    Menghapus seluruh file lama di folder final/ sehingga hanya menyimpan 1 batch output terbaru.
    """
    print("\n[🧹] Membersihkan file lama di folder final/...")
    if os.path.exists(FINAL_DIR):
        for item in os.listdir(FINAL_DIR):
            item_path = os.path.join(FINAL_DIR, item)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
            except Exception as e:
                print(f"⚠️ Gagal menghapus file lama {item}: {e}")

def get_system_font(font_type="bold", size=60):
    """Mencari font tebal yang tersedia di sistem macOS"""
    impact_paths = [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/Library/Fonts/Impact.ttf"
    ]
    arial_bold_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc"
    ]
    check_list = impact_paths if font_type == "impact" else arial_bold_paths
    for p in check_list:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default()
    except Exception:
        return None

def draw_text_with_outline(draw, pos, text, font, fill_color, outline_color, outline_width=6, shadow_offset=(6, 6), shadow_color=(0, 0, 0, 220)):
    """Menggambar teks dengan drop shadow tajam dan outline/stroke tebal"""
    x, y = pos
    # 1. Shadow
    if shadow_offset and shadow_color:
        sx, sy = shadow_offset
        for ox in range(-outline_width, outline_width + 1):
            for oy in range(-outline_width, outline_width + 1):
                draw.text((x + sx + ox, y + sy + oy), text, font=font, fill=shadow_color)
    # 2. Outline / Stroke
    for ox in range(-outline_width, outline_width + 1):
        for oy in range(-outline_width, outline_width + 1):
            if ox != 0 or oy != 0:
                draw.text((x + ox, y + oy), text, font=font, fill=outline_color)
    # 3. Main text
    draw.text((x, y), text, font=font, fill=fill_color)

def create_pro_thumbnail(clean_video_path, thumb_title, thumb_sub, speaker_name, output_thumb_path):
    """
    Membuat poster grafis portrait resolusi tinggi (1080x1920) 
    bergaya kreator pro:
    - Background tech grid gradient gelap + neon cyan rim
    - Foto portrait tokoh close-up (ekstrak frame video beresolusi tajam)
    - Tipografi hook utama raksasa (kuning / cyan tebal) + stroke & drop shadow
    - Sub-hook pemancing klik & badge nama tokoh berbingkai neon
    """
    print(f"\n[🎨] Merender thumbnail poster resolusi tinggi (1080x1920) bergaya Pro...")
    W, H = 1080, 1920
    temp_frame = os.path.join(MAKING_DIR, "thumb_raw_frame.jpg")

    # 1. Ekstrak frame foto berkualitas tinggi pada detik ke-2
    cmd_extract = [
        FFMPEG_EXE, "-y",
        "-ss", "00:00:02",
        "-i", clean_video_path,
        "-vframes", "1",
        "-q:v", "1",
        temp_frame
    ]
    subprocess.run(cmd_extract, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. Siapkan canvas 1080x1920
    canvas = Image.new("RGBA", (W, H), (8, 14, 28, 255))
    draw = ImageDraw.Draw(canvas)

    # Draw Tech Cyber Grid di background
    for x in range(0, W, 70):
        draw.line([(x, 0), (x, H)], fill=(18, 32, 60, 160), width=2)
    for y in range(0, H, 70):
        draw.line([(0, y), (W, y)], fill=(18, 32, 60, 160), width=2)

    # Jika frame berhasil diekstrak, posisikan dan kombinasikan dengan lighting
    if os.path.exists(temp_frame):
        try:
            person_img = Image.open(temp_frame).convert("RGBA")
            # Tingkatkan kontras dan saturasi foto tokoh agar tajam
            enhancer_contrast = ImageEnhance.Contrast(person_img)
            person_img = enhancer_contrast.enhance(1.2)
            enhancer_color = ImageEnhance.Color(person_img)
            person_img = enhancer_color.enhance(1.15)

            # Tempelkan gambar di area bawah canvas (portrait composition)
            person_img = person_img.resize((W, H), Image.Resampling.LANCZOS)
            canvas = Image.alpha_composite(canvas, person_img)
            draw = ImageDraw.Draw(canvas)
        except Exception as e:
            print(f"⚠️ Catatan pengolahan frame: {e}")
        finally:
            if os.path.exists(temp_frame):
                try: os.remove(temp_frame)
                except Exception: pass

    # 3. Vignette & Dark Gradient di bagian atas untuk ruang teks judul tajam
    gradient = Image.new("RGBA", (W, 650), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(gradient)
    for i in range(650):
        alpha = int(240 * (1 - (i / 650) ** 1.5))
        g_draw.line([(0, i), (W, i)], fill=(5, 10, 22, alpha))
    canvas.paste(gradient, (0, 0), gradient)
    draw = ImageDraw.Draw(canvas)

    # 4. Fonts
    font_main = get_system_font("impact", 125)
    font_sub = get_system_font("bold", 48)
    font_badge = get_system_font("bold", 42)

    # 5. Render Teks Sub-Hook di paling atas
    sub_text = (thumb_sub or "INSIGHT TEKNOLOGI VIRAL").strip()
    sub_bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_x = (W - sub_w) // 2
    sub_y = 90
    draw_text_with_outline(draw, (sub_x, sub_y), sub_text, font_sub,
                          fill_color=(255, 255, 255), outline_color=(0, 0, 0), outline_width=4)

    # 6. Render Teks Hook Utama Raksasa (Kuning #FFEE00 / Cyan #00FFFF)
    main_text = (thumb_title or "VIBE CODING").upper().strip()
    # Pecah jika lebih dari 2 kata per baris
    words = main_text.split()
    lines = []
    for i in range(0, len(words), 2):
        lines.append(" ".join(words[i:i+2]))
    
    start_y = 170
    for line in lines:
        line_bbox = draw.textbbox((0, 0), line, font=font_main)
        line_w = line_bbox[2] - line_bbox[0]
        line_h = line_bbox[3] - line_bbox[1]
        line_x = (W - line_w) // 2
        # Teks utama kuning terang menyala dengan outline hitam pekat tebal
        draw_text_with_outline(draw, (line_x, start_y), line, font_main,
                              fill_color=(255, 238, 0), outline_color=(0, 0, 0), outline_width=8,
                              shadow_offset=(8, 8), shadow_color=(0, 0, 0, 240))
        start_y += line_h + 30

    # 7. Render Badge Nama Tokoh di Bagian Bawah
    if speaker_name:
        badge_text = speaker_name.upper().strip()
        b_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
        bw = b_bbox[2] - b_bbox[0]
        bh = b_bbox[3] - b_bbox[1]
        
        box_pad_x = 36
        box_pad_y = 18
        bx = (W - bw) // 2
        by = H - 240
        
        # Rounded Box dengan aksen neon border
        box_coords = [bx - box_pad_x, by - box_pad_y, bx + bw + box_pad_x, by + bh + box_pad_y]
        draw.rounded_rectangle(box_coords, radius=16, fill=(10, 20, 40, 230), outline=(0, 220, 255), width=4)
        draw.text((bx, by), badge_text, font=font_badge, fill=(255, 255, 255))

    # 8. Simpan sebagai file JPEG kualitas 95%
    final_poster = canvas.convert("RGB")
    final_poster.save(output_thumb_path, "JPEG", quality=95)
    print(f"      ✅ Poster Pro berhasil dibuat: {output_thumb_path}")
    return output_thumb_path

def run_process1(custom_query=None):
    query = custom_query or generate_trending_topic()
    v_id, title = search_viral_tech_interview(query)
    if not v_id: return None

    transcript = get_transcript(v_id)
    if not transcript:
        print("❌ Transkrip tidak tersedia pada video ini.")
        return None

    plan = analyze_and_translate_clip(transcript, title)
    if not plan: return None

    start_sec = plan.get("start_time", 60)
    end_sec = plan.get("end_time", start_sec + 35)

    base_id = f"short_{int(time.time())}"
    raw_cut = os.path.join(MAKING_DIR, f"{base_id}_cut.mp4")
    ass_path = os.path.join(MAKING_DIR, f"{base_id}.ass")
    final_mp4 = os.path.join(FINAL_DIR, f"{base_id}.mp4")
    thumb_jpg = os.path.join(FINAL_DIR, f"{base_id}_thumb.jpg")
    metadata_json = os.path.join(FINAL_DIR, "latest_video.json")

    cut_ok = download_cut_crop(v_id, start_sec, end_sec, raw_cut)
    if not cut_ok or not os.path.exists(raw_cut):
        print("❌ Gagal membuat potongan video mentah.")
        return None

    create_ass_subtitle(plan.get("subtitles", []), start_sec, ass_path)

    # Bersihkan folder final/ sebelum merender output terbaru
    clean_final_dir()

    # Ekstrak nama tokoh pembicara dari query atau title
    speaker = ""
    for s_name in ["Sam Altman", "Jensen Huang", "Andrej Karpathy", "Elon Musk", "Ilya Sutskever", "Demis Hassabis", "Mark Zuckerberg", "Dario Amodei"]:
        if s_name.lower() in title.lower() or s_name.lower() in query.lower():
            speaker = s_name
            break
    if not speaker:
        speaker = "Nope Code AI"

    # Buat custom poster pro dari clean video potongan mentah SEBELUM dibakar subtitle
    thumb_title = plan.get("thumb_hook_title") or plan.get("thumbnail_hook") or "VIBE CODING"
    thumb_sub = plan.get("thumb_sub_hook") or "Beneran Bisa Hasilkan Puluhan Juta?"
    create_pro_thumbnail(raw_cut, thumb_title, thumb_sub, speaker, thumb_jpg)

    render_final(raw_cut, ass_path, final_mp4)

    # Bersihkan file kerja sementara di making/
    for tmp_file in [raw_cut, ass_path]:
        if os.path.exists(tmp_file):
            try:
                os.remove(tmp_file)
            except Exception:
                pass

    # Simpan info metadata lengkap untuk dibaca process2.py dan dokumentasi lokal
    info = {
        "video_path": final_mp4,
        "thumbnail_path": thumb_jpg if os.path.exists(thumb_jpg) else "",
        "title": plan.get("title", "Insight AI Tokoh Dunia"),
        "description": plan.get("caption", ""),
        "script_id": plan.get("script_id", ""),
        "script_en": plan.get("script_en", ""),
        "tags": ["Shorts", "AI", "Technology", "NopeCode", "Programming"]
    }
    
    # 1. Simpan format JSON untuk process2.py
    with open(metadata_json, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

    # 2. Simpan format TXT yang enak dibaca langsung
    txt_summary_path = os.path.join(FINAL_DIR, f"{base_id}_detail.txt")
    with open(txt_summary_path, "w", encoding="utf-8") as f:
        f.write(f"JUDUL:\n{info['title']}\n\n")
        f.write(f"DESKRIPSI / CAPTION:\n{info['description']}\n\n")
        f.write(f"THUMBNAIL:\n{info['thumbnail_path']}\n\n")
        f.write(f"NASKAH INDONESIA:\n{info['script_id']}\n\n")
        f.write(f"NASKAH ASLI (EN):\n{info['script_en']}\n\n")
        f.write(f"SUMBER ASLI:\nhttps://www.youtube.com/watch?v={v_id}\n")

    print(f"\n✅ PROCESS 1 SELESAI!")
    print(f"📁 Video Final     : {final_mp4}")
    print(f"🖼️ Thumbnail Final : {thumb_jpg}")
    print(f"📄 Ringkasan Teks  : {txt_summary_path}")
    return info

if __name__ == "__main__":
    run_process1()