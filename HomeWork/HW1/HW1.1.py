# %%

# %%
from preprocessing1 import MelSpectrogram
import tensorflow as tf

# %%
class VAD():
    def __init__(
        self,
        sampling_rate,
        frame_length_in_s,
        num_mel_bins,
        lower_frequency,
        upper_frequency,
        dbFSthres, 
        duration_thres
    ):
        self.frame_length_in_s = frame_length_in_s
        self.mel_spec_processor = MelSpectrogram(
            sampling_rate, frame_length_in_s, frame_length_in_s, num_mel_bins, lower_frequency, upper_frequency
        )
        self.dbFSthres = dbFSthres
        self.duration_thres = duration_thres

    def is_silence(self, audio):
        print("audio in fuction:", audio)
        log_mel_spec = self.mel_spec_processor.get_mel_spec(audio)
        # print("MelSpectrogram", log_mel_spec)
        dbFS = 20 * log_mel_spec
        # print("value of dbFS:", dbFS)
        energy = tf.math.reduce_mean(dbFS, axis=1)

        print("Energy:", energy.numpy())  # Print energy values for debugging

        non_silence = energy > self.dbFSthres
        non_silence_frames = tf.math.reduce_sum(tf.cast(non_silence, tf.float32))
        non_silence_duration = (non_silence_frames + 1) * self.frame_length_in_s

        print("Non-silence frames:", non_silence_frames.numpy())
        print("Non-silence duration:", non_silence_duration.numpy())

        if non_silence_duration > self.duration_thres:
            return 0
        else:
            return 1

# %%
vad_processor = VAD(16000, 0.061, 20, 0, 6000, -35, 0.1)

# %%
# Create a nre Python file a write a script
# that uses the soundevice package to record audio data
# Stop the recording when the Q is pressed
# Measure the output.wav file

import os
import sounddevice as sd
from scipy.io.wavfile import write
from time import time
import argparse as ap

parser = ap.ArgumentParser()
parser.add_argument('--channels', type= int, default=1)
args = parser.parse_args()
# args.parameterName

def callback(indata, frames, callback_time, status):
    global store_audio
    timestamp = time()
    tf_indata = tf.convert_to_tensor(indata, dtype=tf.float32) 
    # tf_indata_normalized = (tf_indata - tf.reduce_min(tf_indata)) / (tf.reduce_max(tf_indata) - tf.reduce_min(tf_indata))
    # tf_indata_normalized  = tf_indata / resolution.max
    tf_indata_normalized = tf_indata / tf.reduce_max(tf.abs(tf_indata))
    print("normal", tf_indata_normalized)
    predicted_silence = vad_processor.is_silence(tf_indata_normalized)
    if predicted_silence == 1 and store_audio is True:
        write(f'{timestamp}.wav', 16000, indata)
        filesize_in_bytes = os.path.getsize(f'{timestamp}.wav')
        filesice_in_kb = filesize_in_bytes/1024
        print(f'Size: {filesice_in_kb} KB')
    
store_audio = True

with sd.InputStream(device=0, channels=args.channels, dtype='int16', samplerate=16000, callback=callback, blocksize=16000):
    while True :
        key = input()
        if key in ('q', 'Q'):
            print('Stop recording.')
            break
        if key in ('p', 'P'):
            store_audio = not store_audio
        
        time.sleep(6)


