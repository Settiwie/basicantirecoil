import time
import win32api
import win32con
import keyboard
import configparser
import os
import threading
import tkinter as tk
from tkinter import messagebox

# Read configuration
config = configparser.ConfigParser()
config_file = 'settings.config'

if not os.path.isfile(config_file):
    print(f"Error: Configuration file '{config_file}' not found.")
    exit(1)

config.read(config_file)

# Initial profile variables
current_profile = 'Profile1'
y_movement = 6.0
toggle_key = 'num lock'
exit_key = 'delete'

# Load initial profile settings
def load_profile(profile):
    global config, x_movement, y_movement, toggle_key, exit_key
    try:
        if profile not in config:
            raise KeyError(f"Profile {profile} not found in the configuration file.")
        x_movement = float(config[profile]['x_movement'])
        y_movement = float(config[profile]['y_movement'])
        toggle_key = config[profile].get('toggle_key', 'num lock')
        exit_key = config[profile].get('exit_key', 'delete')
        update_gui()
        print(f"Loaded {profile} with x_movement: {x_movement}, y_movement: {y_movement}, toggle_key: {toggle_key}, exit_key: {exit_key}")
    except KeyError as e:
        print(f"Error: {e}")
        exit(1)
    except ValueError as e:
        print(f"Error in profile '{profile}': {e}")
        exit(1)

def save_current_profile():
    global config, current_profile, x_movement, y_movement
    config[current_profile]['x_movement'] = str(x_movement)
    config[current_profile]['y_movement'] = str(y_movement)
    config[current_profile]['toggle_key'] = toggle_key
    config[current_profile]['exit_key'] = exit_key
    with open(config_file, 'w') as configfile:
        config.write(configfile)
    print(f"{current_profile} saved with x_movement: {x_movement}, y_movement: {y_movement}, toggle_key: {toggle_key}, exit_key: {exit_key}")

def switch_profile(profile):
    global current_profile
    current_profile = profile
    load_profile(current_profile)

def increase_y_movement():
    global y_movement
    y_movement += 0.1
    update_gui()
    print(f"y_movement increased to: {y_movement}")

def decrease_y_movement():
    global y_movement
    y_movement -= 0.1
    update_gui()
    print(f"y_movement decreased to: {y_movement}")

def control_recoil():
    global toggle_key, exit_key
    recoil_compensation_factor = 2  # Adjust as needed for downward compensation
    quick_start_compensation = 3  # Immediate compensation for the first few bullets
    dynamic_factor = 2  # Start with a strong compensation and decrease it

    shots_fired = 0
    running = False

    keyboard.add_hotkey('k', increase_y_movement)
    keyboard.add_hotkey('l', decrease_y_movement)
    keyboard.add_hotkey('0', save_current_profile)

    while True:
        if keyboard.is_pressed(exit_key):
            break

        if keyboard.is_pressed(toggle_key):
            running = not running
            update_indicator(running)
            print("Recoil Compensation: ", 'On' if running else 'Off')
            time.sleep(0.3)

        if running and win32api.GetAsyncKeyState(0x01) != 0:  # Left mouse button pressed
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(y_movement), 0, 0)
            shots_fired += 1
            dynamic_factor = max(dynamic_factor - 0.05, 1.0)  # Slow down the decrement rate

        if keyboard.is_pressed('i'):
            current_profile_index = int(current_profile.replace("Profile", ""))
            next_profile_index = (current_profile_index % 9) + 1
            switch_profile(f"Profile{next_profile_index}")
            time.sleep(0.3)

        if keyboard.is_pressed('o'):
            current_profile_index = int(current_profile.replace("Profile", ""))
            previous_profile_index = (current_profile_index - 2) % 9 + 1
            switch_profile(f"Profile{previous_profile_index}")
            time.sleep(0.3)

        time.sleep(0.002)

def update_gui():
    y_movement_var.set(f"Y Movement: {y_movement:.1f}")
    profile_var.set(f"Current Profile: {current_profile}")
    name_entry_var.set(config[current_profile].get('name', 'Unnamed'))

def update_indicator(running):
    if running:
        status_indicator.config(bg="green")
        status_var.set("Status: On")
    else:
        status_indicator.config(bg="red")
        status_var.set("Status: Off")

import webbrowser

def open_youtube_link():
    webbrowser.open("https://www.youtube.com/watch?v=uHgt8giw1LY")

def open_config_file():
    os.system("notepad.exe settings.config")

def create_gui():
    global y_movement_var, profile_var, status_var, status_indicator, name_entry_var

    def update_profile_name():
        config[current_profile]['name'] = name_entry_var.get()
        save_current_profile()
        update_gui()
        print(f"Updated name for {current_profile} to: {name_entry_var.get()}")

    root = tk.Tk()
    root.title("Recoil Control")
    root.geometry("400x500")  # Adjusted window size to accommodate all elements
    root.resizable(False, False)

    y_movement_var = tk.StringVar()
    profile_var = tk.StringVar()
    status_var = tk.StringVar()
    name_entry_var = tk.StringVar()

    tk.Label(root, text="Profile Name:").pack(pady=5)
    name_entry = tk.Entry(root, textvariable=name_entry_var)
    name_entry.pack(pady=5)
    tk.Button(root, text="Update Name", command=update_profile_name).pack(pady=5)

    tk.Label(root, textvariable=y_movement_var).pack(pady=5)
    tk.Label(root, textvariable=profile_var).pack(pady=5)
    tk.Label(root, textvariable=status_var).pack(pady=5)

    status_indicator_frame = tk.Frame(root)
    status_indicator_frame.pack(pady=5)
    status_indicator = tk.Label(status_indicator_frame, width=10, height=1, bg="red")
    status_indicator.pack(side=tk.LEFT)
    tk.Button(status_indicator_frame, text="Open Config", command=open_config_file).pack(side=tk.LEFT, padx=5)

    tk.Button(root, text="Increase Y Movement (K)", command=increase_y_movement).pack(pady=5)
    tk.Button(root, text="Decrease Y Movement (L)", command=decrease_y_movement).pack(pady=5)
    tk.Button(root, text="Save Profile (Numpad 0)", command=save_current_profile).pack(pady=5)
    tk.Button(root, text="Next Profile (I)", command=lambda: switch_profile(f"Profile{(int(current_profile.replace('Profile', '')) % 9) + 1}")).pack(pady=5)
    tk.Button(root, text="Previous Profile (O)", command=lambda: switch_profile(f"Profile{(int(current_profile.replace('Profile', '')) - 2) % 9 + 1}")).pack(pady=5)
    tk.Button(root, text="Aimbot", command=open_youtube_link).pack(pady=5)

    update_gui()
    update_indicator(False)

    return root

if __name__ == "__main__":
    root = create_gui()

    recoil_thread = threading.Thread(target=control_recoil)
    recoil_thread.daemon = True
    recoil_thread.start()

    root.after(100, load_profile, current_profile)
    root.mainloop()
