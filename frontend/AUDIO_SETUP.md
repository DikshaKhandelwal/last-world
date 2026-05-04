# Audio Setup for Intro Narration

The intro screen now supports background voice narration. Follow one of the methods below to generate the audio file.

## Audio File Location

Place your MP3 file at: `frontend/public/audio/intro-narration.mp3`

## Option 1: Google Text-to-Speech (Free)

1. Install `gcloud` CLI and authenticate
2. Run:
   ```bash
   gcloud text-to-speech synthesize-speech \
     --text-file=INTRO_NARRATION_TEXT.txt \
     --output-encoding MP3 \
     --language-code en-US \
     --ssml-gender NEUTRAL \
     --pitch 0 \
     --speaking-rate 0.9 \
     --output-audio.encoding MP3 \
     output-audio.mp3
   ```

## Option 2: AWS Polly (Low-cost)

1. Install AWS CLI and configure credentials
2. Create `intro-text.txt` with narration
3. Run:
   ```bash
   aws polly synthesize-speech \
     --text-file intro-text.txt \
     --output-format mp3 \
     --voice-id Joanna \
     --engine standard \
     output.mp3
   ```

## Option 3: OpenAI TTS (Recommended - Best Quality)

1. Install Python and requests:
   ```bash
   pip install openai
   ```

2. Create `generate_audio.py`:
   ```python
   import os
   from openai import OpenAI

   client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

   text = """Meet the Last Model. Imagine the power went out. Your infrastructure fell silent. But a tiny local model kept running on backup power. What could it possibly do?

   The answer isn't that the model does everything. It's that the system around it does most of the work.

   This is a game about survival through engineering, not luck."""

   response = client.audio.speech.create(
       model="tts-1",
       voice="onyx",
       input=text,
       speed=0.9
   )

   response.stream_to_file("intro-narration.mp3")
   print("Audio generated: intro-narration.mp3")
   ```

3. Run:
   ```bash
   OPENAI_API_KEY=sk_... python generate_audio.py
   ```

4. Move `intro-narration.mp3` to `frontend/public/audio/`

## Option 4: ElevenLabs (Premium - Natural Voice)

1. Get API key from https://elevenlabs.io
2. Create `generate_audio.py`:
   ```python
   import requests

   headers = {
       "xi-api-key": "your_elevenlabs_api_key"
   }

   data = {
       "text": "Meet the Last Model. Imagine the power went out...",
       "voice_settings": {
           "stability": 0.5,
           "similarity_boost": 0.75
       }
   }

   response = requests.post(
       "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM",
       headers=headers,
       json=data
   )

   with open("intro-narration.mp3", "wb") as f:
       f.write(response.content)
   ```

3. Run and move audio file to `frontend/public/audio/`

## Option 5: Local Placeholder (Development)

For local development without real audio:

```bash
# Create a silent MP3 placeholder (optional)
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 25 -q:a 9 -acodec libmp3lame frontend/public/audio/intro-narration.mp3
```

## Specs for Generated Audio

- **Format**: MP3
- **Target Duration**: 25-30 seconds (sync with intro text timing)
- **Volume**: Normalized to -14 LUFS
- **Voice**: Neutral, clear, professional narrator
- **Speed**: 0.9x (slightly slower for dramatic effect)
- **Sample Rate**: 44.1 kHz

## Testing

1. Start the frontend dev server: `npm run dev`
2. Navigate to the intro screen
3. Audio should play automatically (browser may require user interaction first)
4. Click "🔊 Mute" button to toggle audio

## Muting & Controls

- Mute button appears in top-right corner
- Audio plays at 60% volume for accessibility
- If narration doesn't start, check browser console for autoplay policy errors

## Notes

- Ensure audio file is MP3 format
- Keep file size under 2MB for fast load
- Test on different browsers for autoplay compatibility
