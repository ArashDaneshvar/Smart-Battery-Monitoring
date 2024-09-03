import sounddevice as sd
from scipy.io import wavfile

from time import time

#######record audio using sounddevice and rec method
# sample_rate = 48000
# duration = 3
# channels = 1

# i = 1
# while True:
#     print("start recording")
#     sample_record = sd.rec(frames= int(sample_rate * duration), samplerate=sample_rate, channels=channels)
#     sd.wait()
#     #Save the file
#     outputfile = f"sample{i}.wav" 
#     wavfile.write(outputfile, sample_rate, sample_record)
#     i+=1
    
#     str = " "
#     while str != "q" or "Q":
#         key = input()
#         if key in ("q","Q"):
#             print("Stop recording")
#             break
#     break



# Rocord audio data using InputStream method (continuous sampling) and store them
sample_rate = 48000
block_size = 48000
device = 0
channels = 1
dtype = "int32"

def callback(indata, frames, callback_time, status):
    timestamp = time()
    wavfile.write(f"{timestamp}.wav", sample_rate, indata)
    print(timestamp)


with sd.InputStream(samplerate= sample_rate, blocksize= block_size, device= 0, channels= channels, dtype=dtype, callback=callback):
    print("Start recording")
    while True:
        key = input()
        if key in ("q", "Q"):
            print("Stop recording")
            break 
