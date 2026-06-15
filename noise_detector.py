import os
os.environ['GPIOZERO_PIN_FACTORY'] = 'rpigpio'  # or 'pigpio'

import sounddevice as sd
from gpiozero import LED
from time import sleep, time
import subprocess
from threading import Thread
import os
import math

#new version speaker (using aplay for Bluetooth compatibility)

# 1. Initialize our LEDs using GPIO Zero
green_led = LED(17)
yellow_led = LED(27)
red_led = LED(22)

# 2. Audio settings
SAMPLE_RATE = 44100  # Standard CD-quality sampling
DURATION = 0.2       # Listen in 0.2-second chunks

# 3. Calibration Thresholds (Adjust these values based on your room test!)
THRESHOLD_LOW = 0.0200   # Levels below this = Quiet (Green)
THRESHOLD_HIGH = 0.1000  # Levels between Low and High = Moderate (Yellow). Above = Loud (Red)

# 4. Audio file for alerts
ALERT_AUDIO_FILE = "/home/benimaru/Noise-Level-Detector/alert_sound.wav"  # Path to your custom audio file

# Time tracking for alert throttling
last_alert_time = 0
ALERT_COOLDOWN = 2  # Only play alert once every 2 seconds

def get_volume(audio_data):
    """Calculates the Root Mean Square (RMS) of the audio chunk to approximate volume."""
    # Calculate mean of squared values
    mean_of_squares = sum(x**2 for x in audio_data) / len(audio_data)
    # Return square root
    rms = math.sqrt(mean_of_squares)
    return rms

def play_alert_sound():
    """Plays the custom alert audio file in a separate thread using aplay."""
    
    if not os.path.exists(ALERT_AUDIO_FILE):
        print(f"⚠️  Alert audio file '{ALERT_AUDIO_FILE}' not found!")
        return
    
    try:
        print(f"🔔 Loading audio file: {ALERT_AUDIO_FILE}")
        print("🔔 Playing Alert Sound (Bluetooth speaker)...")
        # Use aplay to play the audio file
        subprocess.run(['aplay', ALERT_AUDIO_FILE], check=True)
        print("🔔 Alert Sound finished")
    
    except FileNotFoundError:
        print("❌ Error: aplay not found. Please install alsa-utils:")
        print("   sudo apt-get install alsa-utils")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error playing alert sound: {e}")
    except Exception as e:
        print(f"❌ Unexpected error playing alert sound: {e}")

print("🔊 Noise Level Detector is starting... Press Ctrl+C to stop.")
print(f"Alert sound file: {ALERT_AUDIO_FILE}")
print(f"File exists: {os.path.exists(ALERT_AUDIO_FILE)}")

try:
    while True:
        # Record a brief chunk of audio
        recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
        sd.wait()  # Wait until the audio chunk finishes recording
        
        # Calculate current volume amplitude
        volume = get_volume(recording)
        print(f"Current Amplitude RMS: {volume:.4f}")
        
        # Turn all LEDs off before updating to the correct state
        green_led.off()
        yellow_led.off()
        red_led.off()
        
        # Determine which LED to turn on based on the measured volume
        if volume < THRESHOLD_LOW:
            green_led.on()
            print("🟢 Green LED (Quiet)")
        elif THRESHOLD_LOW <= volume < THRESHOLD_HIGH:
            yellow_led.on()
            print("🟡 Yellow LED (Moderate)")
        else:
            red_led.on()
            print("🔴 Red LED (Loud) - Alert should trigger!")
            
            # Only play alert if enough time has passed since last alert
            current_time = time()
            if current_time - last_alert_time > ALERT_COOLDOWN:
                print(f"🔔 Starting alert thread...")
                last_alert_time = current_time
                alert_thread = Thread(target=play_alert_sound, daemon=True)
                alert_thread.start()
            else:
                print(f"⏸️  Alert on cooldown ({ALERT_COOLDOWN}s), skipping...")

except KeyboardInterrupt:
    print("\nShutting down safely. Turning off all LEDs.")
    green_led.off()
    yellow_led.off()
    red_led.off()
