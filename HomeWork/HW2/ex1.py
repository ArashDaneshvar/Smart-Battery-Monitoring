
import tensorflow as tf
import os
import sounddevice as sd
from scipy.io.wavfile import write
from time import time
import argparse as ap
import numpy as np
import psutil
import redis
import time
import uuid
from datetime import datetime

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

class ModelPredictor:
    def __init__(self, model_path):
        self.mel_spec_processor = MelSpectrogram(**PREPROCESSING_ARGS)
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

    def get_prediction(self, input_tensor):

        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        log_mel_spectrogram = self.mel_spec_processor.get_mel_spec(input_tensor)
        log_mel_spectrogram = tf.expand_dims(log_mel_spectrogram, 0)
        log_mel_spectrogram = tf.expand_dims(log_mel_spectrogram, -1)

        self.interpreter.set_tensor(input_details[0]['index'], log_mel_spectrogram)
        self.interpreter.invoke()

        output = self.interpreter.get_tensor(output_details[0]['index'])

        # Find the index of the highest probability class and the corresponding probability
        prediction_index = np.argmax(output)
        prediction_probability = output[0][prediction_index]

        return prediction_index, prediction_probability

PREPROCESSING_ARGS = {
    'sampling_rate': 16000,
    'frame_length_in_s': 0.032,
    'frame_step_in_s': 0.01,
    'num_mel_bins': 20,
    'lower_frequency': 20,
    'upper_frequency': 8000,
}

vad_processor = VAD(16000, 0.032, 10, 0, 6000, -35, 0.1)
model_predictor = ModelPredictor('model13.tflite')

parser = ap.ArgumentParser()
parser.add_argument('--device', type=int, default=0)
parser.add_argument('--host', type=str, default='redis-16255.c267.us-east-1-4.ec2.cloud.redislabs.com')
parser.add_argument('--port', type=int, default= 16255)
parser.add_argument('--username', type=str, default= 'default')
parser.add_argument('--password', type=str, default='J44swf7CVJjEMIjy6tEYuFke5PxxG0kf')
args = parser.parse_args()

REDIS_HOST = args.host
REDIS_PORT = args.port
REDIS_USERNAME = args.username
REDIS_PASSWORD = args.password
redis_client = redis.Redis(host= REDIS_HOST, port= REDIS_PORT, username= REDIS_USERNAME, password= REDIS_PASSWORD)

is_connected = redis_client.ping()
print('Redis Connected:', is_connected)

mac_address = hex(uuid.getnode())

# Set retention periods when creating time series
try:
    redis_client.ts().create(f'{mac_address}:battery', retention_msecs = 86400000)
except redis.exceptions.ResponseError:
    pass

try:
     redis_client.ts().create(f'{mac_address}:power', retention_msecs=86400000)
except redis.exceptions.ResponseError:
    pass

def callback(indata, frames, callback_time, status):
    global check_audio
    global buffer
    global last_tm
    global monitoring  # Declare monitoring as a global variable
    buffer = np.append(buffer, indata)
    if len(buffer) == 16000:
        tf_indata = tf.convert_to_tensor(buffer, dtype=tf.int16) 
        tf_indata = tf.squeeze(tf_indata)
        audio_normalized = tf_indata / tf.int16.max   
        predicted_silence = vad_processor.is_silence(audio_normalized)
        if predicted_silence is 0 and check_audio is True:
            value, probability = model_predictor.get_prediction(audio_normalized)
            print(f'Predicted value: {value}, probability: {probability}')
            if value == 0 and probability > 0.999:
                print('I have to record')
                monitoring = True
            elif value == 1 and probability > 0.99999:
                print('I undesrtood that i dont have to record')
                monitoring = False
            else:
                print('Cant understand what you said')
                pass
        if monitoring == True:
            timestamp = time.time()
            if (timestamp-last_tm) >=1:
                timestamp_ms = int(timestamp * 1000)
                battery_level = psutil.sensors_battery().percent
                power_plugged = int(psutil.sensors_battery().power_plugged)
                redis_client.ts().add(f'{mac_address}:battery', timestamp_ms, battery_level)
                redis_client.ts().add(f'{mac_address}:power', timestamp_ms, power_plugged)
                last_tm = timestamp
            print('Savings')
        buffer = indata
            
check_audio = True
buffer = np.array([], dtype=np.int16)
monitoring = False
last_tm = 0

with sd.InputStream(device=args.device, channels=1, dtype='int16', samplerate=16000, callback=callback, blocksize=8000):
    while True :
        key = input()
        if key in ('q', 'Q'):
            print('Stop recording.')
            break
        if key in ('p', 'P'):
            check_audio = not check_audio
            print('Pause recording.')
    
