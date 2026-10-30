# 🎬 Automated YouTube Shorts Clipper Pipeline (Nope Code)

An intelligent, end-to-end Python automation pipeline designed to autonomously produce viral, vertical **YouTube Shorts (9:16)** from long-form tech interviews and podcasts:

1. **Dynamic YouTube Scraping & Topic Rotation**: Continuously discovers interviews and keynote speeches from global tech leaders (*Sam Altman, Jensen Huang, Andrej Karpathy, Ilya Sutskever, Demis Hassabis, Elon Musk, Mark Zuckerberg, etc.*) using dynamic Gemini search prompts while maintaining a history log (`used_videos.txt`) to avoid duplicates.
2. **AI Virality & Segment Analysis (Google Gemini)**: Analyzes full transcripts, identifies the most impactful 30-45 second segment, crafts high-CTR Indonesian titles (*Curiosity Gap*), structured descriptions, scripts, and synchronized subtitles.
3. **Cinematic 9:16 Dynamic Layout**: Uses an automated blurred vertical background + centered fit foreground via FFmpeg filter graphs, ensuring speakers in wide podcast shots are never awkwardly cropped.
4. **Kinetic Subtitles (.ASS) & BGM Mixing**: Automatically burns stylized kinetic uppercase subtitles with dark outlines and mixes background music smoothly.
5. **High-Res Pro Poster Thumbnail (1080x1920)**: Generates creator-grade portrait thumbnail posters using Pillow—complete with clean un-subtitled frames, giant bold hook typography (yellow/cyan), drop shadows, and neon speaker badges.
6. **One-Click YouTube Data API v3 Upload**: Uploads final MP4 videos with custom metadata and sets the custom thumbnail automatically.

---

## 🚀 Key Features

- 🧠 **AI-Driven Virality Detection**: Gemini analyzes conversation nuances to extract complete, punchy insights without cutting mid-sentence.
- 🎯 **Smart Topic Rotation**: Never repeats the same video twice thanks to automated tracking and dynamic prompt generation.
- 🎨 **Pro-Grade Thumbnails**: Stand out in feeds and search results with 1080x1920 high-resolution posters designed for maximum click-through rate.
- 🧹 **Self-Cleaning Workspace**: Automatically purges temporary render files to keep storage organized.
- 📤 **Automated OAuth 2.0 Uploading**: Integrated YouTube Data API support for direct publishing or staging as private drafts.

---

## 📁 Directory Structure

```text
clipper-youtube/
├── assets/                  # Static assets (e.g., bgm.mp3 for background audio)
├── final/                   # Ready-to-publish outputs (.mp4, .jpg poster, _detail.txt, latest_video.json)
├── making/                  # Temporary render clips, .ass files, and used_videos.txt history
├── main.py                  # Interactive CLI entrypoint for orchestrating Process 1 & Process 2
├── process1.py              # Core pipeline: Scraping, Gemini analysis, FFmpeg editing, & Pro thumbnail
├── process2.py              # YouTube Data API v3 OAuth authentication & upload pipeline
├── .env.example             # Environment variable template
├── requirements.txt         # Project dependencies
└── README.md
```

---

## 🛠️ Prerequisites

- **Python 3.9+** (Python 3.10 or 3.11 recommended)
- **Google Gemini API Key** (Obtain for free at [Google AI Studio](https://aistudio.google.com/))
- **Google Cloud Console Project** (Enable YouTube Data API v3 for automated uploads)

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/nopecode96/python-automation-clipper-nope.git
cd python-automation-clipper-nope
```

### 2. Create & Activate a Virtual Environment
```bash
# macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate

# Windows:
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (`.env`)
Copy `.env.example` to create your local `.env` file:
```bash
cp .env.example .env
```

Open `.env` and fill in your API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GROQ_API_KEY=your_optional_groq_key_here
```

### 5. (Optional) Configure YouTube Data API for Auto-Upload
If you plan to use the automated upload module ([process2.py](process2.py)):
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **YouTube Data API v3**.
3. Create an **OAuth 2.0 Client ID** (Application type: *Desktop App*).
4. Download the JSON credentials file, rename it to `client_secrets.json`, and place it in the project root:
   ```text
   client_secrets.json
   ```
5. *(Optional)* Place an audio track at `assets/bgm.mp3` for automatic background music ducking.

---

## 🎬 How to Run

### Option A: Full Pipeline (Interactive CLI)
```bash
python main.py
```
- Press **ENTER** to automatically select a fresh trending AI topic, or type a custom topic/speaker name.
- Upon completion, the script prompts you whether to upload immediately to YouTube with your preferred visibility (*Private / Unlisted / Public*).

### Option B: Video Generation Only (Process 1)
```bash
python process1.py
```
Outputs generated in the `final/` directory:
- `final/short_<timestamp>.mp4`: 9:16 vertical video with kinetic subtitles & BGM.
- `final/short_<timestamp>_thumb.jpg`: 1080x1920 Pro poster thumbnail.
- `final/short_<timestamp>_detail.txt`: Complete summary containing titles, captions, Indonesian & English scripts, and original source URLs.
- `final/latest_video.json`: Metadata descriptor for automated upload staging.

### Option C: YouTube Upload Only (Process 2)
```bash
python process2.py
```
Reads the latest video info from `final/latest_video.json` and uploads both the video and custom thumbnail to your YouTube channel.

---

## 🔒 Security Notice
Never commit or share your `.env`, `client_secrets.json`, or `token.pickle` files. These sensitive items are ignored by default via [.gitignore](.gitignore).

---

## 👨‍💻 Maintainer
**Nope Code** - *AI, Coding & Tech Automation*
