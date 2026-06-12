#!/usr/bin/env python3
"""
Simple audio test script to verify speaker output on Raspberry Pi.
This will play the alert sound file directly.
"""

import os
import simpleaudio as sa
from time import sleep

# Audio file to test
AUDIO_FILE = "/home/benimaru/Noise-Level-Detector/pcm0808m.wav"

print("🔊 Audio Speaker Test")
print(f"Testing audio file: {AUDIO_FILE}")

# Check if file exists
if not os.path.exists(AUDIO_FILE):
    print(f"❌ Error: File not found at {AUDIO_FILE}")
    print("Please check the file path and try again.")
    exit(1)

print(f"✅ File found!")

try:
    print("\n📢 Loading audio file...")
    wave_obj = sa.WaveObject.from_wave_file(AUDIO_FILE)
    
    print("▶️  Playing audio... (waiting for completion)")
    playback = wave_obj.play()
    
    # Wait for audio to finish playing
    playback.wait_done()
    
    print("✅ Audio playback complete!")
    print("\n🎉 Speaker is working correctly!")
    
except Exception as e:
    print(f"❌ Error during playback: {e}")
    print("Speaker may not be working or audio file is corrupted.")
    exit(1)
