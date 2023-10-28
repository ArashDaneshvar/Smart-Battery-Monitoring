import sounddevice as sd
from scipy.io import wavfile

sample_rate = 48000
block_size = 48000
device = 0
channels = 1
dtype = "int32"

with sd.InputStream(samplerate=sample_rate, blocksize=block_size, device=device, channels=channels, dtype=dtype):
    while True:
        key = input()
        if key in ("q", "Q"):
            print("Stop recording")
            break