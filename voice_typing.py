import keyboard
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import datetime
import threading
import time

is_recording = False
recording = []
samplerate = 44100  # کیفیت ضبط (استاندارد)
buffer_duration = 1  # مدت زمان بافر (ثانیه)

def toggle_recording():
    global is_recording, recording
    if not is_recording:
        print("شروع ضبط صدا...")
        is_recording = True
        recording = []

        # شروع ضبط در یک Thread جدا
        threading.Thread(target=record_audio).start()
    else:
        print("پایان ضبط صدا.")
        is_recording = False
        time.sleep(0.2)  # چند میلی‌ثانیه به سیستم می‌دهیم که ضبط کامل بشه
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
    else:
        print("هیچ صدایی ضبط نشد.")

# اتصال کلید F9 به تابع
keyboard.add_hotkey('f9', toggle_recording)

print("برنامه فعال است. با F9 ضبط را شروع/توقف کن. با ESC از برنامه خارج شو.")
keyboard.wait('esc')
