import json, os, time, tkinter as tk
from tkinter import font as tkfont
from pynput import keyboard

# ===== CONFIG =====
DATA_FILE = "blackflash_data.json"

BLACK_FLASH_TARGET = 0.312
BLACK_FLASH_LOWER = 0.262
BLACK_FLASH_UPPER = 0.362
MAX_FLASH_TIME = BLACK_FLASH_UPPER * 3

# ===== STATE =====
start_time = None
last_time = None
streak = 0
last_grade = "-"
flash_score = 0
consistency_score = 0
last_duration = None

# ===== LOAD DATA =====
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = []

# ===== FUNCTIONS =====
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calculate_consistency():
    global consistency_score
    manual_durations = [d["duration"] for d in data if d["manual"]]
    if len(manual_durations) < 2:
        consistency_score = 0
        return
    import statistics
    std = statistics.stdev(manual_durations)
    consistency_score = max(0, round(100 - (std * 200)))

# Old grade system
def grade_flash(value):
    global flash_score, last_grade
    delta = abs(value - BLACK_FLASH_TARGET)
    if delta <= 0.01:
        last_grade = "PERFECT"
        flash_score = 100
    elif delta <= 0.02:
        last_grade = "GREAT"
        flash_score = 85
    elif delta <= 0.03:
        last_grade = "GOOD"
        flash_score = 70
    elif delta <= 0.04:
        last_grade = "AVERAGE"
        flash_score = 55
    elif delta <= 0.05:
        last_grade = "BAD"
        flash_score = 40
    else:
        last_grade = "HORRIBLE"
        flash_score = 0

def recalc_streak():
    global streak
    streak = 0
    for entry in reversed(data):
        if entry["manual"]:
            streak += 1
        elif BLACK_FLASH_LOWER <= entry["duration"] <= BLACK_FLASH_UPPER:
            streak += 1
        else:
            break

def on_press(key):
    global start_time, last_time, streak, last_grade, flash_score, last_duration
    now = time.perf_counter()
    try:
        if hasattr(key, "char") and key.char is not None:
            k = key.char
            if k == '3':
                if start_time is None:
                    start_time = now
                else:
                    last_time = now - start_time
                    start_time = None
                    last_duration = last_time
                    manual = False
                    grade_flash(last_time)
                    data.append({"duration": last_time, "manual": manual})
                    save_data()
                    recalc_streak()
                    calculate_consistency()
    except:
        pass

# ===== UI =====
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.geometry("380x480+1000+20")

# Transparent background
TRANSPARENT_COLOR = "#d3d3d3"
root.config(bg=TRANSPARENT_COLOR)
root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)

title_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
section_font = tkfont.Font(family="Segoe UI", size=11)
small_font = tkfont.Font(family="Segoe UI", size=9)

def make_section(parent, title):
    section_frame = tk.Frame(parent, bg="#ffffff", bd=2, relief="solid", padx=5, pady=5)
    section_label = tk.Label(section_frame, text=title, font=title_font, fg="black", bg="#ffffff")
    section_label.pack(anchor="w")
    section_frame.pack(fill="x", pady=4)
    return section_frame

# ===== DRAG BAR =====
drag_bar = tk.Frame(root, bg="#222222", height=25)
drag_bar.pack(fill="x", side="top")

drag_data = {"x": 0, "y": 0}
def start_drag(event):
    drag_data["x"] = event.x
    drag_data["y"] = event.y
def do_drag(event):
    x = root.winfo_x() + event.x - drag_data["x"]
    y = root.winfo_y() + event.y - drag_data["y"]
    root.geometry(f"+{x}+{y}")

drag_bar.bind("<Button-1>", start_drag)
drag_bar.bind("<B1-Motion>", do_drag)

# Title on left
title_label = tk.Label(drag_bar, text="Black Flash Tracker", font=title_font, fg="white", bg="#222222")
title_label.pack(side="left", padx=5)

# X button on right
def close_app():
    root.destroy()
close_btn = tk.Button(drag_bar, text="X", command=close_app, bg="#ff5555", fg="white", relief="flat")
close_btn.pack(side="right", padx=5)

# ===== MAIN FRAME =====
frame = tk.Frame(root, bg=TRANSPARENT_COLOR)
frame.pack(fill="both", expand=True, padx=2, pady=(0,2))

# ===== STATS =====
stats_frame = make_section(frame, "STATS")
streak_label = tk.Label(stats_frame, text="STREAK: 0", font=section_font, fg="black", bg="#ffffff")
streak_label.pack(anchor="w")
grade_label = tk.Label(stats_frame, text="Grade: -", font=section_font, fg="black", bg="#ffffff")
grade_label.pack(anchor="w")
score_label = tk.Label(stats_frame, text="Score: 0", font=section_font, fg="black", bg="#ffffff")
score_label.pack(anchor="w")
consistency_label = tk.Label(stats_frame, text="Consistency: 0%", font=section_font, fg="black", bg="#ffffff")
consistency_label.pack(anchor="w")

# ===== FLASH INFO =====
flash_frame = make_section(frame, "FLASH INFO")
last_label = tk.Label(flash_frame, text="Last: -", font=section_font, fg="black", bg="#ffffff")
last_label.pack(anchor="w")
target_label = tk.Label(flash_frame, text=f"Target: {BLACK_FLASH_TARGET}s", font=section_font, fg="black", bg="#ffffff")
target_label.pack(anchor="w")
range_label = tk.Label(flash_frame, text=f"Range: {BLACK_FLASH_LOWER}s - {BLACK_FLASH_UPPER}s", font=section_font, fg="black", bg="#ffffff")
range_label.pack(anchor="w")

# ===== INFORMATION SECTION =====
info_frame = make_section(frame, "HOW TO USE")
info_text = "3 is the default keybind for Yuji's black flash, aswell as the \nstart / stop key."
info_label = tk.Label(info_frame, text=info_text, font=small_font, fg="black", bg="#ffffff", justify="left")
info_label.pack(anchor="w")

# Timer
timer_label = tk.Label(frame, text="0.000 s", font=section_font, fg="black", bg="#ffffff")
timer_label.place(relx=1.0, x=-10, y=10, anchor="ne")

# ===== UI UPDATE =====
def update_ui():
    global start_time, last_duration
    streak_label.config(text=f"STREAK: {streak}")
    grade_label.config(text=f"Grade: {last_grade}")
    score_label.config(text=f"Score: {flash_score}")
    consistency_label.config(text=f"Consistency: {consistency_score}%")
    last_label.config(text=f"Last: {round(last_duration,4)}s" if last_duration else "Last: -")

    if start_time:
        elapsed = time.perf_counter() - start_time
        timer_label.config(text=f"{elapsed:.3f} s")
        if elapsed > MAX_FLASH_TIME:
            start_time = None
            last_time = None
    else:
        timer_label.config(text="0.000 s")
    root.after(20, update_ui)

update_ui()
listener = keyboard.Listener(on_press=on_press)
listener.start()
root.mainloop()
