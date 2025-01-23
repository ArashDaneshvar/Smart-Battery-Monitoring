
import tensorflow as tf

class Spectrogram():
    def __init__(self, sampling_rate, frame_length_in_s, frame_step_in_s):
        self.frame_length = int(frame_length_in_s * sampling_rate)
        self.frame_step = int(frame_step_in_s * sampling_rate)

    def get_spectrogram(self, audio):
        stft = tf.signal.stft(
            audio, 
            frame_length=self.frame_length,
            frame_step=self.frame_step,
            fft_length=self.frame_length
        )
        spectrogram = tf.abs(stft)

        return spectrogram

    def get_spectrogram_and_label(self, audio, label):
        audio = get_spectrogram(audio)

        return spectrogram, label

class MelSpectrogram():
    def __init__(
        self, 
        sampling_rate,
        frame_length_in_s,
        frame_step_in_s,
        num_mel_bins,
        lower_frequency,
        upper_frequency
    ):
        self.spectrogram_processor = Spectrogram(sampling_rate, frame_length_in_s, frame_step_in_s)
        num_spectrogram_bins = self.spectrogram_processor.frame_length // 2 + 1

        self.linear_to_mel_weight_matrix = tf.signal.linear_to_mel_weight_matrix(
            num_mel_bins=num_mel_bins,
            num_spectrogram_bins=num_spectrogram_bins,
            sample_rate=sampling_rate,
            lower_edge_hertz=lower_frequency,
            upper_edge_hertz=upper_frequency
        )

    def get_mel_spec(self, audio):
        spectrogram = self.spectrogram_processor.get_spectrogram(audio)
        mel_spectrogram = tf.matmul(spectrogram, self.linear_to_mel_weight_matrix)
        log_mel_spectrogram = tf.math.log(mel_spectrogram + 1.e-6)

        return log_mel_spectrogram

    def get_mel_spec_and_label(self, audio, label):
        log_mel_spectrogram = self.get_mel_spec(audio)

        return log_mel_spectrogram, label
    
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
        log_mel_spec = self.mel_spec_processor.get_mel_spec(audio)
        dbFS = 20 * log_mel_spec
        energy = tf.math.reduce_mean(dbFS, axis=1)

        non_silence = energy > self.dbFSthres
        non_silence_frames = tf.math.reduce_sum(tf.cast(non_silence, tf.float32))
        non_silence_duration = (non_silence_frames + 1) * self.frame_length_in_s

        if non_silence_duration > self.duration_thres:
            return 0
        else:
            return 1

vad_processor = VAD(16000, 0.032, 10, 0, 6000, -35, 0.1)

import os
import sounddevice as sd
from scipy.io.wavfile import write
from time import time
import argparse as ap
import numpy as np

parser = ap.ArgumentParser()
parser.add_argument('--device', type=int, default=0)
args = parser.parse_args()
# args.parameterName

def callback(indata, frames, callback_time, status):
    global store_audio
    global buffer
    timestamp = time()
    buffer = np.append(buffer, indata)
    if len(buffer) > 16000:
        tf_indata = tf.convert_to_tensor(buffer, dtype=tf.int16) 
        tf_indata = tf.squeeze(tf_indata)
        audio_normalized = tf_indata / tf.int16.max   
        predicted_silence = vad_processor.is_silence(audio_normalized)
        print(f'Predicted silence: {predicted_silence}')
        if predicted_silence is 0 and store_audio is True:
            write(f'{timestamp}.wav', 16000, indata)
            filesize_in_bytes = os.path.getsize(f'{timestamp}.wav')
            filesice_in_kb = filesize_in_bytes/1024
            print(f'Size: {filesice_in_kb} KB')
            buffer = indata
            
store_audio = True
buffer = np.array([], dtype=np.int16)

with sd.InputStream(device=args.device, channels=1, dtype='int16', samplerate=16000, callback=callback, blocksize=8000):
    while True :
        key = input()
        if key in ('q', 'Q'):
            print('Stop recording.')
            break
        if key in ('p', 'P'):
            store_audio = not store_audio
 

