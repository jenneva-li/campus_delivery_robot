import os
import sounddevice as sd
import soundfile as sf
import numpy as np
from scipy import signal

# Set the desired audio device
device_name = "UACDemoV1.0"  # Name of the USB audio device
device_info = sd.query_devices(device_name, 'output')
device_id = device_info['index']
device_sample_rate = device_info['default_samplerate']

# Load the MP3 file
mp3_path = "/home/jade/quickstart/tests/ElevenLabs_2025-02-09T14_23_57_Dave_pre_s50_sb75_se0_b_m2.mp3"  # Replace with your MP3 file path
data, sample_rate = sf.read(mp3_path, dtype='float32')

# Resample if necessary
if sample_rate != device_sample_rate:
    print(f"Resampling from {sample_rate} to {device_sample_rate}")
    number_of_samples = int(round(len(data) * float(device_sample_rate) / sample_rate))
    data = signal.resample(data, number_of_samples)
    sample_rate = device_sample_rate

# Increase the volume (optional)
volume_increase = 500
data = data * volume_increase

try:
    # Play the audio using the specified device
    sd.play(data, samplerate=sample_rate, device=device_id)
    sd.wait()
    print("Audio played successfully")
except sd.PortAudioError as e:
    print(f"Error playing audio: {e}")
    print(f"Supported sample rates for this device: {device_sample_rate}")