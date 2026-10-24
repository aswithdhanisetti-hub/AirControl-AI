"""Step 2 Hand Tracking Test: Verifies MediaPipe Tasks HandLandmarker on live webcam."""
import cv2
import time
import sys
from core.hand_tracker import HandTracker

def run_hand_tracking_test(camera_index=0):
    print("[HandTrackingTest] Initializing HandTracker...")
    try:
        tracker = HandTracker(num_hands=1, min_detection_confidence=0.5)
        print("[HandTrackingTest] HandLandmarker loaded successfully!")
    except Exception as e:
        print(f"[HandTrackingTest] ERROR initializing HandTracker: {e}")
        return False
        
    print(f"[HandTrackingTest] Opening webcam {camera_index}...")
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(camera_index)
        
    if not cap.isOpened():
        print(f"[HandTrackingTest] ERROR: Could not open camera {camera_index}")
        return False
        
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("[HandTrackingTest] Live hand tracking active.")
    print("Hold your hand in front of the camera. Press 'q' or 'Esc' to exit.")
    
    prev_time = time.time()
    fps = 0.0
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
                
            frame_count += 1
            curr_time = time.time()
            if curr_time - prev_time > 0.5:
                fps = frame_count / (curr_time - prev_time)
                frame_count = 0
                prev_time = curr_time
                
            # Mirror frame horizontally
            mirrored_frame = cv2.flip(frame, 1)
            
            # Detect hands
            tracker.find_hands(mirrored_frame)
            landmarks = tracker.get_hand_landmarks(mirrored_frame.shape, hand_index=0)
            handedness, score = tracker.get_handedness(hand_index=0)
            
            # Status overlay
            status_text = "No hand detected"
            status_color = (0, 0, 255)
            
            if landmarks:
                # MediaPipe handedness is inverted relative to mirrored image:
                # When mirrored, physical Right Hand looks like Left to an unmirrored detector.
                display_hand = "Right" if handedness == "Left" else "Left"
                status_text = f"Hand: {display_hand} ({score*100:.0f}%)"
                status_color = (0, 255, 0)
                tracker.draw_landmarks(mirrored_frame, landmarks)
                
            # Render HUD
            cv2.putText(
                mirrored_frame,
                f"AirControl AI - Hand Tracking [FPS: {fps:.1f}]",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )
            cv2.putText(
                mirrored_frame,
                status_text,
                (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                status_color,
                2,
                cv2.LINE_AA
            )
            cv2.putText(
                mirrored_frame,
                "Press 'q' or 'Esc' to exit test",
                (10, 95),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (180, 180, 180),
                1,
                cv2.LINE_AA
            )
            
            if cv2.getWindowProperty("AirControl AI - Hand Tracking Test", cv2.WND_PROP_VISIBLE) < 1:
                print("[HandTrackingTest] Window close button clicked. Exiting cleanly...")
                break
                
            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):
                print("[HandTrackingTest] Exit key pressed. Closing cleanly...")
                break
                
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[HandTrackingTest] Cleanup finished.")
        
    return True

if __name__ == "__main__":
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    success = run_hand_tracking_test(idx)
    sys.exit(0 if success else 1)
