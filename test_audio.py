#!/usr/bin/env python3
"""
Simple audio test script to verify speaker output on Raspberry Pi.
This will play the alert sound file directly using aplay (works with Bluetooth speakers).
"""

import os
import subprocess

# Audio file to test
AUDIO_FILE = "/home/benimaru/Noise-Level-Detector/pcm0808m.wav"

print("🔊 Audio Speaker Test (Bluetooth Compatible)")
print(f"Testing audio file: {AUDIO_FILE}")

# Check if file exists
if not os.path.exists(AUDIO_FILE):
    print(f"❌ Error: File not found at {AUDIO_FILE}")
    print("Please check the file path and try again.")
    exit(1)

print(f"✅ File found!")

try:
    print("\n▶️  Playing audio with aplay...")
    subprocess.run(['aplay', AUDIO_FILE], check=True)
    
    print("✅ Audio playback complete!")
    print("\n🎉 Speaker is working correctly!")
    
except subprocess.CalledProcessError as e:
    print(f"❌ Error during playback: {e}")
    print("Speaker may not be working or audio file is corrupted.")
    exit(1)
except FileNotFoundError:
    print("❌ Error: aplay not found. Please install alsa-utils:")
    print("   sudo apt-get install alsa-utils")
    exit(1)
