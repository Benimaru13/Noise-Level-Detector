import sounddevice as sd
import numpy as np
from gpiozero import LED
from time import sleep

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

def get_volume(audio_data):
    """Calculates the Root Mean Square (RMS) of the audio chunk to approximate volume."""
    rms = np.sqrt(np.mean(audio_data**2))
    return rms

print("🔊 Noise Level Detector is starting... Press Ctrl+C to stop.")

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
        elif THRESHOLD_LOW <= volume < THRESHOLD_HIGH:
            yellow_led.on()
        else:
            red_led.on()

except KeyboardInterrupt:
    print("\nShutting down safely. Turning off all LEDs.")
    green_led.off()
    yellow_led.off()
    red_led.off()
