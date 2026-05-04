# Free Audio Generation Setup (Google Cloud TTS)

## Quick Start

Google Cloud Text-to-Speech is **completely free** for personal/development use.

### Step 1: Install Package
```bash
pip install google-cloud-texttospeech
```

### Step 2: Set Up Google Cloud Credentials

1. Go to: https://console.cloud.google.com
2. Click **Create Project**, name it "last-model"
3. Search for **"Text-to-Speech API"** and click **Enable**
4. Go to **IAM & Admin → Service Accounts**
5. Click **Create Service Account**
6. Name: `audio-generator`
7. Click **Create and Continue**
8. Grant role: **Editor** (or just "Cloud Text-to-Speech Client")
9. Skip optional steps, click **Done**
10. Click the service account you just created
11. Go to **Keys** tab → **Add Key → Create New Key → JSON**
12. Save the JSON file somewhere safe (e.g., `~/google-credentials.json`)

### Step 3: Set Environment Variable

**On macOS/Linux:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/google-credentials.json"
```

**On Windows (PowerShell):**
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\google-credentials.json"
```

**On Windows (CMD):**
```cmd
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\google-credentials.json
```

### Step 4: Generate Audio

```bash
python generate_intro_audio.py
```

The audio will be saved to: `frontend/public/audio/intro-narration.mp3`

### Step 5: Test

Start your dev server:
```bash
cd frontend && npm run dev
```

Visit http://localhost:5173 (or your dev URL) and the intro should have narration with a mute button.

---

## Free Tier Limits

Google Cloud Text-to-Speech free tier includes:
- **4 million characters per month** (plenty for this project)
- High-quality neural voices
- No credit card required after setup

---

## Troubleshooting

**Error: "Error initializing Google TTS client"**
- Make sure `GOOGLE_APPLICATION_CREDENTIALS` points to your JSON file correctly
- Verify the file exists and is readable

**Error: "Permission denied"**
- Go back to Google Console and verify the Service Account has "Cloud Text-to-Speech Client" role
- Wait a minute for permissions to propagate

**Audio file not created**
- Check that `frontend/public/audio/` directory was created
- Run the script again with `python generate_intro_audio.py`

---

Done! Your intro will now have free, high-quality AI narration. 🎙️
