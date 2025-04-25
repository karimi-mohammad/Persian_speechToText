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
import speech_recognition as sr
import pyperclip  # برای کپی کردن متن به کلیپ‌بورد
import json

# تنظیمات عمومی
is_recording = False
recording = []
samplerate = 44100
buffer_duration = 1
selected_mode = None
RECORDINGS_DIR = "recordings"
mic_boost = 1.0  # ضریب تقویت صدا (۱ برابر = بدون تقویت)
copy_to_clipboard_enabled = True  # پرچم برای فعال یا غیرفعال کردن کپی به کلیپ‌بورد

# ساخت پوشه ضبط‌ها
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# انتخاب مدل
def choose_model_ui(main_root):
    def select(option):
        global selected_mode
        selected_mode = option
        model_window.destroy()

    model_window = tk.Toplevel(main_root)
    model_window.title("انتخاب مدل تشخیص گفتار")
    model_window.geometry("300x150")

    label = tk.Label(model_window, text="مدل مورد نظر را انتخاب کنید:")
    label.pack(pady=10)

    btn1 = tk.Button(model_window, text="مدل آفلاین (Vosk)", command=lambda: select("offline"))
    btn1.pack(pady=5)

    btn2 = tk.Button(model_window, text="مدل آنلاین (Google)", command=lambda: select("online"))
    btn2.pack(pady=5)

# شروع/توقف ضبط
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
        audio = np.concatenate(recording, axis=0).astype(np.float32)
        audio *= mic_boost  # اعمال تقویت صدا

        # جلوگیری از overflow
        audio = np.clip(audio, -32768, 32767).astype(np.int16)

        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{RECORDINGS_DIR}/record_{now}.wav"
        wav.write(filename, samplerate, audio)
        print(f"فایل صدا ذخیره شد: {filename}")
        time.sleep(1)
        abs_filename = os.path.abspath(filename)
        process_audio(abs_filename)
        update_file_count_label()

def process_audio(filename):
    print(f"پردازش فایل: {filename}")
    final_text = ""
    
    if selected_mode == "offline":
        wf = wave.open(filename, "rb")
        model = Model(r"I:\computer\My projs\other\persian_stt\vosk-model-small-fa-0.42")
        rec = KaldiRecognizer(model, wf.getframerate())
        print("مدل آفلاین فعال است...")
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            rec.AcceptWaveform(data)
        result = rec.FinalResult()
        print(f"نتیجه مدل آفلاین: {result}")

        # استخراج متن از خروجی JSON
        try:
            final_text = json.loads(result)["text"]
        except json.JSONDecodeError:
            print("خطا در پردازش خروجی JSON مدل آفلاین.")
        
    elif selected_mode == "online":
        r = sr.Recognizer()
        with sr.AudioFile(filename) as source:
            audio = r.record(source)
        try:
            print("مدل آنلاین فعال است...")
            final_text = r.recognize_google(audio, language="fa-IR")
            print("نتیجه:", final_text)
        except sr.UnknownValueError:
            print("نتوانست گفتار را تشخیص دهد.")
        except sr.RequestError as e:
            print(f"خطا در اتصال به Google: {e}")

    # اگر کپی به کلیپ‌بورد فعال است، متن را کپی می‌کند
    if copy_to_clipboard_enabled:
        copy_to_clipboard(final_text)

def copy_to_clipboard(text):
    """متن ورودی را به کلیپ‌بورد کپی می‌کند"""
    pyperclip.copy(text)
    print("متن به کلیپ‌بورد کپی شد.")

# دریافت تعداد فایل‌های ضبط‌شده
def get_recording_count():
    files = [f for f in os.listdir(RECORDINGS_DIR) if f.endswith('.wav')]
    return len(files)

# آپدیت لیبل تعداد فایل‌ها
def update_file_count_label():
    count = get_recording_count()
    if file_count_label:
        file_count_label.config(text=f"تعداد فایل‌های ضبط‌شده: {count}")

# حذف همه فایل‌های ضبط‌شده
def delete_all_recordings():
    for file in os.listdir(RECORDINGS_DIR):
        if file.endswith(".wav"):
            os.remove(os.path.join(RECORDINGS_DIR, file))
    update_file_count_label()
    messagebox.showinfo("پاک‌سازی", "همه فایل‌های ضبط‌شده حذف شدند.")

# آپدیت لیبل تقویت صدا
def update_boost_label(val):
    global boost_label
    global mic_boost
    mic_boost = float(val)
    boost_label.config(text=f"تقویت میکروفون: {mic_boost:.1f}x")

# فعال/غیرفعال کردن کپی به کلیپ‌بورد
def toggle_copy_to_clipboard():
    global copy_to_clipboard_enabled
    copy_to_clipboard_enabled = not copy_to_clipboard_enabled
    if copy_to_clipboard_enabled:
        copy_clipboard_btn.config(text="غیرفعال کردن کپی به کلیپ‌بورد")
    else:
        copy_clipboard_btn.config(text="فعال کردن کپی به کلیپ‌بورد")

# اجرای برنامه اصلی
def main():
    global file_count_label, boost_label, copy_clipboard_btn

    root = tk.Tk()
    root.title("برنامه تشخیص گفتار")
    root.geometry("400x250")

    label = tk.Label(root, text="با فشردن F9 شروع/پایان ضبط را کنترل کن.\nبرای خروج ESC را بزن.", font=("Tahoma", 11))
    label.pack(pady=10)

    file_count_label = tk.Label(root, text="", font=("Tahoma", 11))
    file_count_label.pack(pady=10)
    update_file_count_label()

    delete_btn = tk.Button(root, text="🗑️ حذف همه فایل‌ها", command=delete_all_recordings, bg="red", fg="white")
    delete_btn.pack(pady=5)

    # انتخاب مدل
    choose_model_ui(root)

    # تنظیمات تقویت صدا
    boost_label = tk.Label(root, text="تقویت میکروفون: 1.0x", font=("Tahoma", 10))
    boost_label.pack(pady=(10, 0))

    boost_slider = tk.Scale(root, from_=1.0, to=5.0, resolution=0.1, orient="horizontal", command=update_boost_label)
    boost_slider.set(1.0)
    boost_slider.pack()

    # دکمه برای فعال/غیرفعال کردن کپی به کلیپ‌بورد
    copy_clipboard_btn = tk.Button(root, text="غیرفعال کردن کپی به کلیپ‌بورد", command=toggle_copy_to_clipboard, bg="orange")
    copy_clipboard_btn.pack(pady=10)

    # کلیدها
    keyboard.add_hotkey('f9', toggle_recording)

    def wait_for_esc():
        keyboard.wait('esc')
        print("خروج از برنامه...")
        root.quit()

    threading.Thread(target=wait_for_esc, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    file_count_label = None
    boost_label = None  # تعریف متغیر boost_label قبل از استفاده
    copy_clipboard_btn = None  # تعریف متغیر برای دکمه کپی به کلیپ‌بورد
    main()
