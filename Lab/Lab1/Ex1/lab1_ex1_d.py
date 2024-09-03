# Rocord audio data using InputStream method (continuous sampling) and store them
# Modify the script to let the user to disable/enable the audio storage by pressing the P key.

import sounddevice as sd
from scipy.io import wavfile
from time import time


sample_rate = 48000
block_size = 48000
device = 0
channels = 1
dtype = "int32"

def callback(indata, frames, callback_time, status):
    global audio_store
    if audio_store == True:
        timestamp = time()
        wavfile.write(f"{timestamp}.wav", sample_rate, indata)
        print(timestamp)

audio_store = True

with sd.InputStream(samplerate=sample_rate, blocksize=block_size, device=device, channels=channels, dtype=dtype, callback=callback):
    print("Start recording")
    while True:
        key = input()
        if key in ("q", "Q"):
            print("Stop recording")
            break 
        if key in ("p", "P"):
            audio_store = not audio_store

