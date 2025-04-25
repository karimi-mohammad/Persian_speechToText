import keyboard
import datetime

def log_f9():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] F9 key was pressed")

# وقتی کلید F9 فشار داده شد، تابع log_f9 اجرا بشه
keyboard.add_hotkey('f9', log_f9)

print("Listening for F9 key... Press ESC to stop.")

# منتظر بمون تا کاربر ESC رو بزنه
keyboard.wait('esc')
