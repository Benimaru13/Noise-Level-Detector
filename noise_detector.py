import os
os.environ['GPIOZERO_PIN_FACTORY'] = 'rpigpio'  # or 'pigpio'

import sounddevice as sd
from gpiozero import LED
from time import sleep
import simpleaudio as sa
from threading import Thread
import os
import math

#new version speaker 

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
ALERT_AUDIO_FILE = "/home/benimaru/Noise-Level-Detector/pcm0808m.wav"  # Path to your custom audio file

# Global variable to track if alert is currently playing
alert_playing = False
current_playback = None

def get_volume(audio_data):
    """Calculates the Root Mean Square (RMS) of the audio chunk to approximate volume."""
    # Calculate mean of squared values
    mean_of_squares = sum(x**2 for x in audio_data) / len(audio_data)
    # Return square root
    rms = math.sqrt(mean_of_squares)
    return rms

def play_alert_sound():
    """Plays the custom alert audio file in a separate thread."""
    global alert_playing, current_playback
    
    if not os.path.exists(ALERT_AUDIO_FILE):
        print(f"⚠️  Alert audio file '{ALERT_AUDIO_FILE}' not found!")
        return
    
    try:
        print(f"🔔 Loading audio file: {ALERT_AUDIO_FILE}")
        # Load and play the audio file
        wave_obj = sa.WaveObject.from_wave_file(ALERT_AUDIO_FILE)
        print("🔔 Audio file loaded, starting playback...")
        current_playback = wave_obj.play()
        alert_playing = True
        print("🔔 Playing Alert Sound")
        
        # Wait for playback to finish
        current_playback.wait_done()
        alert_playing = False
        print("🔔 Alert Sound finished")
    
    except Exception as e:
        print(f"❌ Error playing alert sound: {e}")
        alert_playing = False

def stop_alert_sound():
    """Stops the currently playing alert sound."""
    global alert_playing, current_playback
    
    if current_playback and alert_playing:
        current_playback.stop()
        alert_playing = False
        print("🔕 Alert Sound Stopped")

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
            stop_alert_sound()
        elif THRESHOLD_LOW <= volume < THRESHOLD_HIGH:
            yellow_led.on()
            print("🟡 Yellow LED (Moderate)")
            stop_alert_sound()
        else:
            red_led.on()
            print("🔴 Red LED (Loud) - Alert should trigger!")
            # Play alert sound in a separate thread (non-blocking)
            if not alert_playing:
                print("🔔 Starting alert thread...")
                alert_thread = Thread(target=play_alert_sound, daemon=True)
                alert_thread.start()
            else:
                print("⏸️  Alert already playing, skipping...")

except KeyboardInterrupt:
    print("\nShutting down safely. Turning off all LEDs.")
    stop_alert_sound()
    green_led.off()
    yellow_led.off()
    red_led.off()
