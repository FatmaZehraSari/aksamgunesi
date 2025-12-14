import customtkinter as ctk
import screen_brightness_control as sbc
import threading
import time
import tkinter as tk
import os
import sys 
from ctypes import windll, byref, Structure, c_ushort, c_void_p

# --- RESOURCE PATH FUNCTION ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- DPI AWARENESS SETUP ---
try:
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# ==========================================
# HARDWARE GAMMA CONTROL
# ==========================================
class GAMMARAMP(Structure):
    _fields_ = [("Red", c_ushort * 256), ("Green", c_ushort * 256), ("Blue", c_ushort * 256)]

class HardwareGamma:
    def __init__(self):
        self.gdi32 = windll.gdi32
        self.user32 = windll.user32

    def set_gamma(self, r, g, b):
        ramp = GAMMARAMP()
        for i in range(256):
            val = i * 257
            ramp.Red[i]   = min(65535, int(val * r))
            ramp.Green[i] = min(65535, int(val * g))
            ramp.Blue[i]  = min(65535, int(val * b))
        
        hdc = self.user32.GetDC(None)
        if not hdc: return False
        success = self.gdi32.SetDeviceGammaRamp(hdc, byref(ramp))
        self.user32.ReleaseDC(None, hdc)
        return bool(success)

# ==========================================
# SOFTWARE OVERLAY (FALLBACK)
# ==========================================
class SoftwareOverlay(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.overrideredirect(True) 
        self.attributes("-topmost", True, "-alpha", 0.0) 
        self.config(bg="#FF4500") 
        self.state('zoomed') 
        self.make_click_through()

    def make_click_through(self):
        try:
            hwnd = windll.user32.GetParent(self.winfo_id()) or self.winfo_id()
            old_style = windll.user32.GetWindowLongW(hwnd, -20)
            windll.user32.SetWindowLongW(hwnd, -20, old_style | 0x80000 | 0x20)
        except: pass

    def set_opacity(self, value):
        self.attributes("-alpha", value * 0.20)

# ==========================================
# MAIN APPLICATION
# ==========================================
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AksamGunesiApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AksamGunesi")
        self.geometry("340x420") 
        self.resizable(False, False)
        
        # --- LOAD ICON SAFELY ---
        icon_file = "aksam_gunesi_icon.ico"
        icon_path = resource_path(icon_file)
        
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"Icon error: {e}")
        else:
            print(f"⚠️ Icon not found: {icon_path}")
        
        # --- INITIALIZE ENGINES ---
        self.hw_engine = HardwareGamma()
        self.sw_overlay = None
        self.active_method = "Scanning..."
        
        self.after(500, self.init_overlay)
        
        self.target_bright = 100
        self.target_rgb = [1.0, 1.0, 1.0]
        self.is_running = False

        # --- UI LAYOUT ---
        self.lbl_title = ctk.CTkLabel(self, text="Atmosfer / Atmosphere", font=("Roboto Medium", 20))
        self.lbl_title.pack(pady=(20, 5))
        
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(pady=(0, 10))
        
        self.info_lbl = ctk.CTkLabel(self.info_frame, text="⏳ Taranıyor / Scanning...", 
                                     font=("Arial", 11), text_color="gray")
        self.info_lbl.pack()

        self.create_btn("☀️ Odak / Focus", "Tam Beyaz / Full White", 
                        100, [1.0, 1.0, 1.0], "#F59E0B", "#D97706")
        
        self.create_btn("⛅ Yumuşak / Soft", "Kırık Beyaz / Warm White", 
                        80, [1.0, 0.95, 0.90], "#3B82F6", "#2563EB")
        
        self.create_btn("🌙 Gece / Night", "Göz Koruma / Eye Care", 
                        40, [1.0, 0.90, 0.70], "#4B5563", "#374151")
        
        self.create_btn("🌅 Akşam Güneşi / Evening Sun", "Tam Sıcaklık / Deep Warm", 
                        20, [1.0, 0.80, 0.50], "#BE123C", "#9F1239")
        
        ctk.CTkButton(self, text="↺ Sıfırla / Reset", fg_color="transparent", 
                      border_width=1, border_color="gray", text_color=("gray10", "gray90"), 
                      font=("Roboto", 12),
                      height=30, width=140, command=self.reset).pack(side="bottom", pady=25)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def init_overlay(self):
        if not self.sw_overlay:
            self.sw_overlay = SoftwareOverlay(self)
            if self.hw_engine.set_gamma(1.0, 1.0, 1.0):
                self.active_method = "Hardware"
                self.info_lbl.configure(text="✅ Donanım Modu / Hardware Mode", text_color="green")
            else:
                self.active_method = "Software"
                self.info_lbl.configure(text="⚠️ Yazılım Modu / Software Mode", text_color="#E67E22")

    def create_btn(self, txt, sub, b, rgb, col, hover_col):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(pady=4) 
        btn_text = f"{txt}\n({sub})"
        btn = ctk.CTkButton(f, text=btn_text, font=("Roboto", 13, "bold"),
                            height=45, width=290, 
                            fg_color=col, hover_color=hover_col, corner_radius=14,
                            command=lambda: self.start_anim(b, rgb))
        btn.pack()

    def start_anim(self, b, rgb):
        if self.is_running: return
        threading.Thread(target=self.animate, args=(b, rgb), daemon=True).start()

    def animate(self, target_b, target_rgb):
        self.is_running = True
        try: start_b = sbc.get_brightness(display=0)[0]
        except: start_b = 50
        
        steps = 30
        warmth_level = 1.0 - target_rgb[2] 
        
        for i in range(steps + 1):
            p = i / steps
            cur_b = start_b + (target_b - start_b) * p
            try: sbc.set_brightness(int(cur_b))
            except: pass
            
            if "Hardware" in self.active_method:
                cr = 1.0 
                cg = 1.0 - (1.0 - target_rgb[1]) * p
                cb = 1.0 - (1.0 - target_rgb[2]) * p
                if not self.hw_engine.set_gamma(cr, cg, cb):
                    self.active_method = "Software"
                    self.info_lbl.configure(text="⚠️ HDR -> Software Mode", text_color="#E67E22")
            
            if "Software" in self.active_method and self.sw_overlay:
                self.sw_overlay.set_opacity(warmth_level * p)
            
            time.sleep(0.02)
        self.is_running = False

    def reset(self):
        self.start_anim(100, [1.0, 1.0, 1.0])

    def on_close(self):
        try: self.hw_engine.set_gamma(1.0, 1.0, 1.0)
        except: pass
        if self.sw_overlay: self.sw_overlay.destroy()
        self.destroy()

if __name__ == "__main__":
    app = AksamGunesiApp()
    app.mainloop()