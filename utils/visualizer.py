"""HUD and Debugging Visualizer for AirControl AI.
Displays recognized gesture, per-finger OPEN/FOLDED states, stability counter, and safety controls.
"""
import cv2
import numpy as np


class Visualizer:
    @staticmethod
    def draw_hud(
        frame: np.ndarray,
        fps: float,
        gesture_info: dict,
        is_armed: bool,
        last_action_desc: str,
        active_window_status: str,
        handedness_str: str = "Unknown"
    ) -> np.ndarray:
        """Draws a clean, high-visibility debugging HUD overlay."""
        h, w = frame.shape[:2]
        
        # 1. Top Navigation Bar: Title, FPS, Handedness, ARM/DISARM
        top_bar_h = 44
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, top_bar_h), (20, 20, 25), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
        
        cv2.putText(
            frame,
            "AirControl AI",
            (12, 28),
            cv2.FONT_HERSHEY_DUPLEX,
            0.68,
            (0, 255, 200),
            2,
            cv2.LINE_AA
        )
        
        # FPS & Handedness
        cv2.putText(
            frame,
            f"FPS: {fps:.1f} | Hand: {handedness_str}",
            (180, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (190, 190, 190),
            1,
            cv2.LINE_AA
        )
        
        # Spacebar Arm / Disarm Indicator (Top Right)
        arm_text = "ARMED" if is_armed else "DISARMED [Space to Arm]"
        arm_bg = (0, 160, 40) if is_armed else (0, 60, 200)
        cv2.rectangle(frame, (w - 235, 6), (w - 10, 38), arm_bg, -1)
        cv2.putText(
            frame,
            arm_text,
            (w - 228, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )
        
        # 2. Gesture Recognition Status (Upper Left)
        raw_g = gesture_info.get('raw_gesture', 'UNKNOWN')
        stable_g = gesture_info.get('stable_gesture', 'UNKNOWN')
        stability_count = gesture_info.get('stability_count', 0)
        is_latched = gesture_info.get('is_latched', False)
        
        action_labels = {
            "CLOSED_FIST": "PAUSE (k)",
            "OPEN_PALM": "PLAY (k)",
            "THUMBS_UP": "VOLUME UP (up)",
            "PEACE_SIGN": "MUTE/UNMUTE (m)",
            "ROCK_SIGN": "NEXT VIDEO (Shift+N)"
        }
        
        # Display Stable Gesture Badge
        if stable_g in action_labels:
            badge_text = f"STABLE: {stable_g} -> {action_labels[stable_g]}"
            badge_color = (0, 255, 100)  # Bright green
        elif raw_g != "UNKNOWN" and raw_g != "NO_HAND":
            badge_text = f"STABILIZING: {raw_g} ({stability_count}/10)"
            badge_color = (0, 200, 255)  # Amber
        else:
            badge_text = f"GESTURE: {raw_g}"
            badge_color = (180, 180, 180)  # Neutral grey
            
        cv2.putText(
            frame,
            badge_text,
            (12, 74),
            cv2.FONT_HERSHEY_DUPLEX,
            0.65,
            badge_color,
            2,
            cv2.LINE_AA
        )
        
        # Latch State Display
        if is_latched:
            latch_text = "LATCH: TRIGGERED (Release hand to reset)"
            latch_color = (0, 220, 255)
        else:
            latch_text = "LATCH: READY (Awaiting stable gesture)"
            latch_color = (150, 255, 150)
            
        cv2.putText(
            frame,
            latch_text,
            (12, 98),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.46,
            latch_color,
            1,
            cv2.LINE_AA
        )
        
        # 3. Per-Finger OPEN / FOLDED Debugging Panel
        # Requirement 7: Display each finger's OPEN/FOLDED state on the camera window
        finger_states = gesture_info.get('finger_states', {})
        if isinstance(finger_states, list):
            f_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
            finger_states = {k: v for k, v in zip(f_names, finger_states)}
            
        start_y = 126
        cv2.putText(frame, "Finger Debug:", (12, start_y), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 200, 200), 1, cv2.LINE_AA)
        
        finger_order = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
        col_x = 12
        for idx, f_name in enumerate(finger_order):
            is_open = finger_states.get(f_name, False)
            state_str = "OPEN" if is_open else "FOLDED"
            state_col = (0, 255, 0) if is_open else (70, 70, 160)
            
            # Draw small rectangular indicator
            box_x = col_x + idx * 82
            box_y = start_y + 10
            cv2.rectangle(frame, (box_x, box_y), (box_x + 76, box_y + 22), (35, 35, 45), -1)
            cv2.rectangle(frame, (box_x, box_y), (box_x + 76, box_y + 22), state_col, 1)
            
            label = f"{f_name[:3]}:{state_str}"
            cv2.putText(frame, label, (box_x + 4, box_y + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.38, state_col, 1, cv2.LINE_AA)
            
        # 4. Bottom Bar: Last Triggered Action & Active Window Target
        bottom_bar_h = 44
        overlay_bottom = frame.copy()
        cv2.rectangle(overlay_bottom, (0, h - bottom_bar_h), (w, h), (15, 15, 20), -1)
        cv2.addWeighted(overlay_bottom, 0.8, frame, 0.2, 0, frame)
        
        cv2.putText(
            frame,
            f"Action: {last_action_desc}",
            (12, h - 26),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 200),
            1,
            cv2.LINE_AA
        )
        
        cv2.putText(
            frame,
            active_window_status,
            (12, h - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (160, 160, 160),
            1,
            cv2.LINE_AA
        )
        
        return frame
