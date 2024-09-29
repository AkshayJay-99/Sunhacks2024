import sounddevice as sd
import wave
import numpy as np
from openai import OpenAI
import os
import pyttsx3                                                                                                                                                                                                         
from dotenv import load_dotenv
from pathlib import Path
import configparser
# import threading
# import keyboard


config = configparser.ConfigParser()
config.read('config.ini')

# load_dotenv(Path("D:\Amogh\SunHacks\.env"))

OPENAI_API_KEY = config['openaiapikey']['api']
# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

#Initialize speech engine
engine = pyttsx3.init()

# Step 1: Record Audio
def record_audio(duration=10, sample_rate=16000):
    print("Recording...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()  # Wait for the recording to complete
    print("Recording complete.")
    return audio

# Step 2: Save Audio to WAV File
def save_audio_to_wav(audio_data, filename, sample_rate=16000):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono channel
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())

# Step 3: Transcribe Audio Using Whisper API
def transcribe_audio(filename):
    with open(filename, 'rb') as audio_file:
        response = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1"
        )
    return response.text

def speak(text):
    engine.say(text)
    engine.runAndWait()

#WHEN RECORD BUTTON IS PRESSED
count = 0
audio_data = record_audio(duration=10)
save_audio_to_wav(audio_data, "output.wav")
transcription = transcribe_audio("output.wav")
speak(transcription)
print("Transcription:", transcription)