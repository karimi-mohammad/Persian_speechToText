import tkinter as tk
from tkinter import messagebox
import keyboard
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import datetime
import threading
import time
from vosk import Model, KaldiRecognizer
import wave
import os
import speech_recognition as sr  # برای مدل آنلاین

# تنظیمات عمومی
is_recording = False
recording = []
samplerate = 44100
buffer_duration = 1
selected_mode = None  # online یا offline

# تابع UI برای انتخاب مدل
def choose_model():
    def select(option):
        global selected_mode
        selected_mode = option
        root.destroy()

    root = tk.Tk()
    root.title("انتخاب مدل تشخیص گفتار")
    root.geometry("300x150")

    label = tk.Label(root, text="مدل مورد نظر را انتخاب کنید:")
    label.pack(pady=10)

    btn1 = tk.Button(root, text="مدل آفلاین (Vosk)", command=lambda: select("offline"))
    btn1.pack(pady=5)

    btn2 = tk.Button(root, text="مدل آنلاین (Google)", command=lambda: select("online"))
    btn2.pack(pady=5)

    root.mainloop()

# تابع شروع ضبط
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
        time.sleep(1)
        abs_filename = os.path.abspath(filename)
        process_audio(abs_filename)

def process_audio(filename):
    print(f"پردازش فایل: {filename}")
    
    if selected_mode == "offline":
        wf = wave.open(filename, "rb")
        model = Model("I:\computer\My projs\other\persian_stt/vosk-model-small-fa-0.42")
        rec = KaldiRecognizer(model, wf.getframerate())
        print("مدل آفلاین فعال است...")
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            rec.AcceptWaveform(data)
        print(rec.FinalResult())

    elif selected_mode == "online":
        r = sr.Recognizer()
        with sr.AudioFile(filename) as source:
            audio = r.record(source)
        try:
            print("مدل آنلاین فعال است...")
            text = r.recognize_google(audio, language="fa-IR")
            print("نتیجه:", text)
        except sr.UnknownValueError:
            print("نتوانست گفتار را تشخیص دهد.")
        except sr.RequestError as e:
            print(f"خطا در اتصال به Google: {e}")

# اجرای UI و انتخاب مدل
choose_model()

# اتصال کلید F9 به ضبط
keyboard.add_hotkey('f9', toggle_recording)

print("برنامه فعال است. با F9 ضبط را شروع/توقف کن. با ESC از برنامه خارج شو.")
keyboard.wait('esc')
