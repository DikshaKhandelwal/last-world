#!/usr/bin/env python3
"""
Generate intro narration audio using OpenAI TTS API.
Requires: OPENAI_API_KEY environment variable

Install: pip install openai
Usage: python generate_intro_audio.py
"""

import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai module not found. Install with: pip install openai")
    sys.exit(1)

# Intro narration text
INTRO_TEXT = """> CONNECTING TO INFERENCE CLUSTER...............
[TIMEOUT]
> CONNECTING TO BACKUP CLUSTER..................
[TIMEOUT]

Meet the Last Model. 

Imagine the power went out. Your infrastructure fell silent. 

But a tiny local model kept running on backup power. 

What could it possibly do?

The answer isn't that the model does everything. 

It's that the system around it does most of the work.

This is a game about survival through engineering, not luck.

Here's the setup: We're running Qwen, a lightweight 0.6 billion parameter model, locally through Ollama. 

That's a model that fits on a modest machine. 

If Ollama goes down, we have a fallback to Groq, a fast inference service.

But the story isn't about model power. 

It's about what happens after the model gives you an answer.

The game presents five levels. Each one is a different kind of task.

Level One: Code Review. You paste code, and the system finds bugs.

Level Two: Argument Analysis. You give it an argument, and the system detects logical fallacies.

Level Three: Behavioral Forensics. A transcript of team members discussing an incident.

Level Four: Data Integrity. Upload a CSV, and the system detects impossible values.

Level Five: Crisis Communication. Rewrite technical incident summaries for the public.

Each level follows the same pattern: naive model output, deterministic system pass, and a proof panel.

The magic isn't in the model. It's in the layers of verification around it.

That's how you survive the blackout.

That's the Last Model."""

def generate_audio():
    """Generate intro narration audio using OpenAI TTS."""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY=sk_...")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    output_path = Path(__file__).parent / 'frontend' / 'public' / 'audio' / 'intro-narration.mp3'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("Generating intro narration audio...")
    print(f"Output: {output_path}")
    
    try:
        response = client.audio.speech.create(
            model="tts-1-hd",  # HD quality
            voice="onyx",       # Deep, neutral narrator voice
            input=INTRO_TEXT,
            speed=0.95         # Slightly slower for dramatic effect
        )
        
        response.stream_to_file(str(output_path))
        
        file_size = output_path.stat().st_size / (1024 * 1024)
        print(f"✓ Audio generated successfully!")
        print(f"✓ File size: {file_size:.2f} MB")
        print(f"✓ Location: {output_path}")
        print("\nAudio will play automatically when you visit the intro screen.")
        
    except Exception as e:
        print(f"Error generating audio: {e}")
        sys.exit(1)

if __name__ == '__main__':
    generate_audio()
