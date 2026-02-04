import json, time, threading, keyboard, sys
import win32api
from ctypes import WinDLL
import numpy as np
from mss import mss as mss_module

def exiting():
    print("Sortie du programme...")
    sys.exit()

user32, kernel32, shcore = (
    WinDLL("user32", use_last_error=True),
    WinDLL("kernel32", use_last_error=True),
    WinDLL("shcore", use_last_error=True),
)

shcore.SetProcessDpiAwareness(2)
WIDTH, HEIGHT = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

ZONE = 5
GRAB_ZONE = (
    int(WIDTH / 2 - ZONE),
    int(HEIGHT / 2 - ZONE),
    int(WIDTH / 2 + ZONE),
    int(HEIGHT / 2 + ZONE),
)

class triggerbot:
    def __init__(self):
        self.sct = mss_module()
        self.triggerbot = False
        self.triggerbot_toggle = True
        self.exit_program = False
        self.toggle_lock = threading.Lock()

        try:
            with open('config.json') as json_file:
                data = json.load(json_file)

            print("Configuration chargée:", data)

            self.trigger_hotkey = int(data["trigger_hotkey"], 16)
            self.always_enabled = data["always_enabled"]
            self.trigger_delay = data["trigger_delay"]
            self.base_delay = data["base_delay"]
            self.color_tolerance = data["color_tolerance"]
            self.R, self.G, self.B = (250, 100, 250)  # Couleur cible (violet)
        except Exception as e:
            print(f"Erreur lors du chargement du fichier config.json : {e}")
            exiting()

    def cooldown(self):
        time.sleep(0.1)
        with self.toggle_lock:
            self.triggerbot_toggle = True
            if self.triggerbot:
                kernel32.Beep(440, 75)
                kernel32.Beep(700, 100)
            else:
                kernel32.Beep(440, 75)
                kernel32.Beep(200, 100)

    def searcherino(self):
        try:
            img = np.array(self.sct.grab(GRAB_ZONE))
            print("Image capturée.")

            pmap = np.array(img)
            pixels = pmap.reshape(-1, 4)

            color_mask = (
                (pixels[:, 0] > self.R - self.color_tolerance) & (pixels[:, 0] < self.R + self.color_tolerance) &
                (pixels[:, 1] > self.G - self.color_tolerance) & (pixels[:, 1] < self.G + self.color_tolerance) &
                (pixels[:, 2] > self.B - self.color_tolerance) & (pixels[:, 2] < self.B + self.color_tolerance)
            )
            matching_pixels = pixels[color_mask]

            if self.triggerbot and len(matching_pixels) > 0:
                delay_percentage = self.trigger_delay / 100.0
                actual_delay = self.base_delay + self.base_delay * delay_percentage

                print(f"Tir détecté ! Attente de {actual_delay:.3f} secondes")
                time.sleep(actual_delay)

                keyboard.press("k")
                time.sleep(0.05)  # Délai pour éviter le blocage
                keyboard.release("k")

        except Exception as e:
            print(f"Erreur dans searcherino : {e}")

    def toggle(self):
        try:
            if keyboard.is_pressed("f10"):
                with self.toggle_lock:
                    if self.triggerbot_toggle:
                        self.triggerbot = not self.triggerbot
                        print(f"Triggerbot activé: {self.triggerbot}")
                        self.triggerbot_toggle = False
                        threading.Thread(target=self.cooldown, daemon=True).start()

            if keyboard.is_pressed("ctrl+shift+x"):
                print("Sortie demandée par l'utilisateur.")
                self.exit_program = True
                exiting()

        except Exception as e:
            print(f"Erreur dans toggle : {e}")

    def hold(self):
        while True:
            try:
                while win32api.GetAsyncKeyState(self.trigger_hotkey) < 0:
                    self.triggerbot = True
                    self.searcherino()
                else:
                    time.sleep(0.1)

                if keyboard.is_pressed("ctrl+shift+x"):
                    print("Sortie demandée par l'utilisateur.")
                    self.exit_program = True
                    exiting()

            except Exception as e:
                print(f"Erreur dans hold : {e}")

    def starterino(self):
        try:
            while not self.exit_program:
                if self.always_enabled:
                    self.toggle()
                    if self.triggerbot:
                        self.searcherino()
                    else:
                        time.sleep(0.1)
                else:
                    self.hold()

        except Exception as e:
            print(f"Erreur dans starterino : {e}")

triggerbot().starterino()
