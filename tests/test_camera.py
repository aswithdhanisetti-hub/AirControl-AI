"""Step 1 Webcam Test: Verifies camera access, DirectShow backend, mirroring, and safe exit."""
import cv2
import time
import sys

def run_webcam_test(camera_index=0):
    print(f"[CameraTest] Attempting to open camera index {camera_index} with DirectShow (CAP_DSHOW)...")
    
    # Use cv2.CAP_DSHOW on Windows for instant initialization without 3s MSMF delay
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print(f"[CameraTest] Failed to open with CAP_DSHOW, trying default backend...")
        cap = cv2.VideoCapture(camera_index)
        
    if not cap.isOpened():
        print(f"[CameraTest] ERROR: Could not open camera at index {camera_index}.")
        print("[CameraTest] Troubleshooting tips:")
        print("  1. Ensure no other application (Zoom, Teams, Discord, Browser) is using the webcam.")
        print("  2. Ensure Windows Camera privacy settings allow desktop apps to access the camera:")
        print("     Settings -> Privacy & Security -> Camera -> Allow desktop apps to access your camera.")
        print("  3. If using an external USB camera, try camera_index=1.")
        return False
        
    # Set preferred resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[CameraTest] Camera opened successfully! Resolution: {actual_w}x{actual_h}")
    print("[CameraTest] Press 'q' or 'Esc' in the preview window to exit.")
    
    prev_time = time.time()
    fps = 0.0
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("[CameraTest] Warning: Failed to read frame from camera stream.")
                time.sleep(0.05)
                continue
                
            frame_count += 1
            curr_time = time.time()
            dt = curr_time - prev_time
            if dt > 0.5:
                fps = frame_count / dt
                frame_count = 0
                prev_time = curr_time
                
            # Mirror the frame horizontally for intuitive interaction
            mirrored_frame = cv2.flip(frame, 1)
            
            # Draw HUD overlay
            cv2.putText(
                mirrored_frame,
                f"AirControl AI - Webcam Test [FPS: {fps:.1f}]",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )
            cv2.putText(
                mirrored_frame,
                "Press 'q' or 'Esc' to exit test",
                (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (200, 200, 200),
                1,
                cv2.LINE_AA
            )
            
            cv2.imshow("AirControl AI - Webcam Test", mirrored_frame)
            
            if cv2.getWindowProperty("AirControl AI - Webcam Test", cv2.WND_PROP_VISIBLE) < 1:
                print("[CameraTest] Window close button clicked. Exiting cleanly...")
                break
                
            # Exit on 'q' or Esc (ASCII 27)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):
                print("[CameraTest] Exit key pressed. Closing cleanly...")
                break
                
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[CameraTest] Camera released and windows destroyed successfully.")
        
    return True

if __name__ == "__main__":
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    success = run_webcam_test(idx)
    sys.exit(0 if success else 1)
