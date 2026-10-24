"""AirControl AI - Hand Gesture YouTube Controller
Main application entry point integrating tracking, robust gesture recognition, HUD, and safety-armed YouTube controller.
"""
import sys
import time
import cv2
import numpy as np

from utils.model_downloader import ensure_model_downloaded
from core.hand_tracker import HandTracker
from core.gesture_engine import GestureEngine
from core.controller import YouTubeController
from utils.visualizer import Visualizer


def run_aircontrol(camera_index: int = 0):
    print("=" * 60)
    print("       AirControl AI - Hand Gesture YouTube Controller      ")
    print("=" * 60)
    
    # 1. Verify Model Asset
    print("\n[Step 1] Verifying Hand Landmark Model...")
    try:
        model_path = ensure_model_downloaded()
        print(f"[Step 1] Model verified: {model_path}")
    except Exception as e:
        print(f"[Step 1] Model verification failed: {e}")
        return False
        
    # 2. Initialize Hand Tracker
    print("\n[Step 2] Initializing MediaPipe Tasks HandLandmarker...")
    try:
        tracker = HandTracker(num_hands=1, min_detection_confidence=0.55)
        print("[Step 2] HandLandmarker loaded successfully!")
    except Exception as e:
        print(f"[Step 2] Tracker initialization failed: {e}")
        return False
        
    # 3. Initialize Gesture Engine (10-frame persistence) & YouTube Controller
    print("\n[Step 3] Initializing Gesture Engine (10-Frame Persistence) and Safety Controller...")
    gesture_engine = GestureEngine(persistence_frames=10)
    controller = YouTubeController()
    
    # 4. Open Webcam with fallback
    print(f"\n[Step 4] Opening Webcam (Index {camera_index})...")
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"[Step 4] DirectShow failed, attempting default backend...")
        cap = cv2.VideoCapture(camera_index)
        
    # Automatic fallback to index 1 if index 0 fails
    if not cap.isOpened() and camera_index == 0:
        print("[Step 4] Index 0 failed. Trying camera index 1...")
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(1)
        
    if not cap.isOpened():
        print(f"[Step 4] ERROR: Could not open camera {camera_index}.")
        print("Please check that no other application is using your webcam.")
        return False
        
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("\n" + "=" * 60)
    print("AirControl AI is Running!")
    print("Target Gesture Mappings:")
    print("  ✊ Closed Fist  -> PAUSE (k)")
    print("  ✋ Open Palm    -> PLAY (k)")
    print("  👍 Thumbs Up    -> VOLUME UP (up)")
    print("  ✌️ Peace Sign   -> MUTE/UNMUTE (m)")
    print("  🤟 Rock Sign    -> NEXT VIDEO (Shift+N)")
    print("Controls:")
    print("  [Space] : Toggle ARM / DISARM safety clutch")
    print("  [q/Esc] : Exit cleanly")
    print("=" * 60 + "\n")
    
    fps = 0.0
    frame_count = 0
    prev_time = time.time()
    last_action_desc = "None"
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
                
            frame_count += 1
            curr_time = time.time()
            if curr_time - prev_time > 0.4:
                fps = frame_count / (curr_time - prev_time)
                frame_count = 0
                prev_time = curr_time
                
            # Mirror frame horizontally so movement feels natural like a mirror
            mirrored_frame = cv2.flip(frame, 1)
            
            # Detect Hands
            tracker.find_hands(mirrored_frame)
            landmarks = tracker.get_hand_landmarks(mirrored_frame.shape, hand_index=0)
            raw_handedness, hand_score = tracker.get_handedness(hand_index=0)
            
            # MediaPipe inverted handedness on mirrored feed
            if raw_handedness:
                physical_hand = "Right" if raw_handedness == "Left" else "Left"
                handedness_str = f"{physical_hand} ({hand_score*100:.0f}%)"
            else:
                handedness_str = "None"
            
            # Draw landmarks if present
            if landmarks:
                tracker.draw_landmarks(mirrored_frame, landmarks)
                
            # Process Gestures with 10-frame persistence and hand-relative geometry
            gesture_info = gesture_engine.process_frame(landmarks)
            
            # Check Active Window
            is_youtube_active, win_title = controller.get_active_window_status()
            win_display = f"Active Window: {win_title[:32]}" if win_title else "No Active Window"
            
            # Dispatch YouTube Actions (Triggered ONCE upon reaching 10-frame stability)
            if gesture_info['is_new_trigger']:
                stable_g = gesture_info['stable_gesture']
                success, msg = controller.trigger_action(stable_g)
                last_action_desc = msg
                
            # Draw HUD with full debugging panel
            hud_frame = Visualizer.draw_hud(
                frame=mirrored_frame,
                fps=fps,
                gesture_info=gesture_info,
                is_armed=controller.is_armed,
                last_action_desc=last_action_desc,
                active_window_status=win_display,
                handedness_str=handedness_str
            )
                
            cv2.imshow("AirControl AI", hud_frame)
            
            # 1. Process Windows OS message queue FIRST so close events are registered
            key = cv2.waitKey(1) & 0xFF
            
            # 2. Check if user clicked the red [X] close button on the window
            try:
                if cv2.getWindowProperty("AirControl AI", cv2.WND_PROP_VISIBLE) < 1:
                    print("[AirControl] Window [X] close button clicked. Exiting cleanly...")
                    break
            except Exception:
                break
                
            # 3. Exit on 'q' or Esc (27)
            if key in (ord('q'), 27):
                print("[AirControl] Exit key pressed ('q' or Esc). Exiting cleanly...")
                break
                
            # Toggle Arm/Disarm on Spacebar (32)
            elif key == 32:
                armed = controller.toggle_arm()
                last_action_desc = "ARMED" if armed else "DISARMED"
                    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[AirControl] Webcam released and windows closed cleanly.")
        
    return True


if __name__ == "__main__":
    cam_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    run_aircontrol(cam_id)
