import keyboard
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import datetime
import threading
import time
from vosk import Model, KaldiRecognizer, SetLogLevel
import wave
import os
import speech_recognition as sr  # برای مدل آنلاین

# --- تنظیمات ---
is_recording = False
recording = []
samplerate = 44100
buffer_duration = 1

# انتخاب نوع مدل
use_online = None
while use_online not in ['1', '2']:
    use_online = input("مدل مورد نظر را انتخاب کن:\n1. آفلاین (Vosk)\n2. آنلاین (Google Speech)\n>>> ")

use_online = use_online == '2'

if not use_online:
    # بارگذاری مدل Vosk (فقط اگر آفلاین انتخاب شده)
    model = Model("I:\\computer\\My projs\\other\\persian_stt/vosk-model-small-fa-0.42")

def toggle_recording():
    global is_recording, recording
    if not is_recording:
        print("شروع ضبط صدا...")
        is_recording = True
        recording = []
        threading.Thread(target=record_audio).start()
    else:
        print("پایان ضبط صدا.")
        is_recording = False
        time.sleep(0.2)
        save_recording()

def record_audio():
    global recording
    while is_recording:
        data = sd.rec(int(buffer_duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()
        recording.append(data)

def save_recording():
    if recording:
        audio = np.concatenate(recording, axis=0)
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"record_{now}.wav"
        wav.write(filename, samplerate, audio)
        print(f"فایل صدا ذخیره شد: {filename}")
        abs_filename = os.path.abspath(filename)
        process_audio(abs_filename)

def process_audio(filename):
    print(f"پردازش فایل: {filename}")
    
    if use_online:
        print("تشخیص گفتار با استفاده از مدل آنلاین...")
        recognizer = sr.Recognizer()
        with sr.AudioFile(filename) as source:
            audio_data = recognizer.record(source)
            try:
                result = recognizer.recognize_google(audio_data, language="fa-IR")
                print("متن تشخیص‌داده‌شده:", result)
            except sr.UnknownValueError:
                print("تشخیص ممکن نبود.")
            except sr.RequestError:
                print("خطا در اتصال به سرویس آنلاین.")
    else:
        print("تشخیص گفتار با استفاده از مدل آفلاین (Vosk)...")
        wf = wave.open(filename, "rb")
        rec = KaldiRecognizer(model, wf.getframerate())
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            rec.AcceptWaveform(data)
        print(rec.FinalResult())

# هات‌کی برای ضبط
keyboard.add_hotkey('f9', toggle_recording)

print("برنامه فعال است. با F9 ضبط را شروع/توقف کن. با ESC خارج شو.")
keyboard.wait('esc')
