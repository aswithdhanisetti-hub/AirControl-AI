"""Step 4 YouTube Controller with strict gesture mappings, Spacebar Arm/Disarm safety & focus guard."""
import time
from typing import Optional, Tuple
import pyautogui
import pygetwindow as gw

# Enforce PyAutoGUI safety standards
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.04


class YouTubeController:
    def __init__(self):
        # Spacebar Arm/Disarm safety switch (Starts DISARMED by default)
        self.is_armed: bool = False
        self.last_action_time: float = 0.0
        self.action_cooldown: float = 0.4  # Min seconds between actions
        self.last_action_name: str = "None"
        
        # Gesture actions mapping:
        # - Closed Fist = Pause ('k')
        # - Open Palm = Play ('k')
        # - Thumbs Up = Volume Up ('up')
        # - Peace Sign = Mute/Unmute ('m')
        # - Rock Sign = Next Video (Shift + N)
        self.gesture_actions = {
            "CLOSED_FIST": ('press', 'k', "PAUSE (Closed Fist)"),
            "OPEN_PALM": ('press', 'k', "PLAY (Open Palm)"),
            "THUMBS_UP": ('press', 'up', "VOLUME UP (Thumbs Up)"),
            "PEACE_SIGN": ('press', 'm', "MUTE/UNMUTE (Peace Sign)"),
            "ROCK_SIGN": ('shift_combo', 'n', "NEXT VIDEO (Rock Sign)")
        }

    def toggle_arm(self) -> bool:
        """Toggles the Arm/Disarm safety state."""
        self.is_armed = not self.is_armed
        print(f"[Controller] {'*** ARMED (Gestures Active) ***' if self.is_armed else '--- DISARMED (Gestures Paused) ---'}")
        return self.is_armed

    def get_active_window_status(self) -> Tuple[bool, str]:
        """Checks if the currently active OS window is YouTube.
        Returns (is_youtube_active, window_title).
        """
        try:
            active_win = gw.getActiveWindow()
            if not active_win or not active_win.title:
                return False, "No Active Window"
            title = active_win.title.strip()
            is_youtube = "- YouTube" in title or "YouTube -" in title
            return is_youtube, title
        except Exception as e:
            return False, f"Window Check Error: {e}"

    def trigger_action(self, action_name: str) -> Tuple[bool, str]:
        """Dispatches keyboard hotkeys to YouTube if all safety checks pass.
        Returns (success: bool, status_message: str).
        """
        # Rule 4: Never execute a YouTube action for UNKNOWN or NO_HAND
        if action_name in ("UNKNOWN", "NO_HAND", None):
            return False, "UNKNOWN (No Action)"

        # Rule 8: Safety Arm Switch Check
        if not self.is_armed:
            return False, "DISARMED (Press Space to Arm)"

        # Active Window Check
        is_youtube, current_title = self.get_active_window_status()
        if not is_youtube:
            short_title = current_title[:28] + "..." if len(current_title) > 28 else current_title
            return False, f"BLOCKED: Not YouTube [{short_title}]"

        # Cooldown check
        now = time.time()
        if (now - self.last_action_time) < self.action_cooldown:
            return False, "COOLDOWN"

        # Lookup action
        if action_name not in self.gesture_actions:
            return False, f"Ignored gesture: {action_name}"

        action_type, key, desc = self.gesture_actions[action_name]

        try:
            if action_type == 'press':
                pyautogui.press(key)
            elif action_type == 'shift_combo':
                # Hold Shift and press 'n' (YouTube shortcut for Next Video)
                pyautogui.keyDown('shift')
                time.sleep(0.04)
                pyautogui.press(key)
                time.sleep(0.04)
                pyautogui.keyUp('shift')

            self.last_action_time = now
            self.last_action_name = desc
            print(f"[Controller] EXECUTED: {desc}")
            return True, f"Triggered: {desc}"
        except pyautogui.FailSafeException:
            print("[Controller] FAILSAFE TRIGGERED! Moving mouse into corner halted inputs.")
            self.is_armed = False
            return False, "FAILSAFE TRIGGERED"
        except Exception as e:
            print(f"[Controller] Error executing {desc}: {e}")
            return False, f"Input Error: {e}"
