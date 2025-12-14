# AksamGunesi

![Python](https://img.shields.io/badge/Python-3.13.5-3776AB?style=flat&logo=python&logoColor=white) ![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat&logo=windows&logoColor=white)

AksamGunesi is a lightweight desktop application for Windows that adjusts screen color temperature in a reliable way, even when HDR is enabled. It is built to handle cases where Windows Night Light or similar tools stop working due to driver or HDR limitations. The project is written in Python and uses CustomTkinter for a simple, modern interface.

AksamGunesi focuses on one problem: making the screen more comfortable to look at in the evening without breaking contrast or black levels.

---

## Why AksamGunesi?

On many Windows laptops and monitors, HDR blocks access to hardware-level color controls. As a result, most night light tools either disable themselves or produce washed-out colors.

AksamGunesi works around this by using a hybrid approach:

- **Hardware Mode** The app first tries to adjust the monitor’s RGB values directly using the Win32 GDI API. This produces the cleanest result and preserves true blacks.

- **Software Mode** If hardware access is blocked (for example, when HDR is active), the app automatically switches to a low-opacity overlay that reduces blue light without heavily affecting contrast.

This switching happens automatically and requires no user intervention.

---

## Features

- **Evening Sun (Akşam Güneşi)** A deep warm color profile designed for late-night use, reducing eye strain significantly.

- **Hybrid Engine** Works regardless of HDR state or GPU driver behavior.

- **Low Resource Usage** Designed to run quietly in the background with minimal CPU and memory usage. UI responsiveness is maintained using threading.

- **Natural Color Output** Uses carefully limited RGB values to avoid the overly orange or muddy look common in many overlay-based solutions.

---

## Technical Overview

- **Language:** Python 3.13.5  
- **GUI:** CustomTkinter  
- **Windows API:** ctypes, windll  
- **Libraries:** screen_brightness_control, threading, Pillow  

---

## Installation

Python is not required for the end user.

1. Open the **Releases** section on the right side of the repository.
2. Download `AksamGunesi.exe`.
3. Run the application directly.

---

![aksam_gunesi](https://github.com/user-attachments/assets/4468ecf6-cf4e-499b-8380-0abd1c052023)


---

Developed by F. Zehra Sarı
