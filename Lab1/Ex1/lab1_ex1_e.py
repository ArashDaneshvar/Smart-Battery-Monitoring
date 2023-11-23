# Modify the script to introduce the following parameters as command-line arguments (use the
# argparse package):
# • Resolution (str): int16 or int32
# • Sampling Rate in Hertz (int)
# • Number of Channels (int)
# • File duration in seconds (int)

import sounddevice as sd
from scipy.io import wavfile
from time import time
import argparse


# sample_rate = 48000
# block_size = 48000
device = 0
# channels = 1
# dtype = "int32"


parser = argparse.ArgumentParser()
parser.add_argument("--resolution",type=str, default="int32", help="Resolution (str)")
parser.add_argument("--samplerate",type=int, default=48000, help="Sampling Rate in Hertz")
parser.add_argument("--channels",type=int, default=1, help="Number of Channels")
parser.add_argument("--duration",type=int, default=1, help="File duration in seconds(int)")
args = parser.parse_args()

def callback(indata, frames, callback_time, status):
    global audio_store
    if audio_store == True:
        timestamp = time()
        wavfile.write(f"{timestamp}.wav", args.samplerate, indata)
        print(timestamp)

audio_store = True
block_size = args.duration * args.samplerate

with sd.InputStream(samplerate=args.samplerate, blocksize=block_size, device=device, channels=args.channels, dtype=args.duration, callback=callback):
    print("Start recording")
    while True:
        key = input()
        if key in ("q", "Q"):
            print("Stop recording")
            break 
        if key in ("p", "P"):
            audio_store = not audio_store