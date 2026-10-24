"""Comprehensive Test Suite verifying:
1. Closed Fist = Pause (k)
2. Open Palm = Play (k)
3. Thumbs Up = Volume Up (up)
4. Peace Sign = Mute/Unmute (m)
5. Ambiguous poses = UNKNOWN (never triggers)
6. 10-frame persistence buffer
7. Trigger once per gesture (latching) and neutral reset
"""
import os
import sys

# Ensure project root is in Python module search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.gesture_engine import GestureEngine
from core.controller import YouTubeController


def generate_hand_landmarks(finger_states: dict, is_thumbs_up: bool = False, is_left_hand: bool = False):
    """Generates synthetic 21 3D landmarks for testing geometric rules."""
    lms = [{'norm_x': 0.5, 'norm_y': 0.5, 'z': 0.0} for _ in range(21)]
    
    # Wrist (0) and Middle MCP (9)
    lms[0] = {'norm_x': 0.5, 'norm_y': 0.8, 'z': 0.0}
    lms[9] = {'norm_x': 0.5, 'norm_y': 0.5, 'z': 0.0}
    
    # Knuckles (MCPs):
    # Left vs Right hand mirrors the horizontal placement of knuckles
    flip = -1.0 if is_left_hand else 1.0
    lms[5] = {'norm_x': 0.5 - 0.08 * flip, 'norm_y': 0.52, 'z': 0.0}  # Index MCP
    lms[13] = {'norm_x': 0.5 + 0.06 * flip, 'norm_y': 0.52, 'z': 0.0} # Ring MCP
    lms[17] = {'norm_x': 0.5 + 0.12 * flip, 'norm_y': 0.55, 'z': 0.0} # Pinky MCP
    
    finger_indices = [
        ('Index', 5, 6, 7, 8),
        ('Middle', 9, 10, 11, 12),
        ('Ring', 13, 14, 15, 16),
        ('Pinky', 17, 18, 19, 20)
    ]
    
    for name, m, p, d, t in finger_indices:
        base_x = lms[m]['norm_x']
        if finger_states.get(name, False):
            # Extended finger (tip is far from wrist, y points upwards)
            lms[p] = {'norm_x': base_x, 'norm_y': 0.40, 'z': 0.0}
            lms[d] = {'norm_x': base_x, 'norm_y': 0.30, 'z': 0.0}
            lms[t] = {'norm_x': base_x, 'norm_y': 0.20, 'z': 0.0}
        else:
            # Folded finger (curled into palm, tip is close to MCP/wrist)
            lms[p] = {'norm_x': base_x, 'norm_y': 0.56, 'z': 0.0}
            lms[d] = {'norm_x': base_x, 'norm_y': 0.61, 'z': 0.0}
            lms[t] = {'norm_x': base_x, 'norm_y': 0.63, 'z': 0.0}
            
    # Configure Thumb (1, 2, 3, 4):
    thumb_dir = -1.0 * flip
    if is_thumbs_up:
        # Thumbs Up: Thumb pointing straight UP towards the top of the frame
        lms[1] = {'norm_x': 0.5 + 0.10 * thumb_dir, 'norm_y': 0.72, 'z': 0.0}
        lms[2] = {'norm_x': 0.5 + 0.12 * thumb_dir, 'norm_y': 0.62, 'z': 0.0}
        lms[3] = {'norm_x': 0.5 + 0.12 * thumb_dir, 'norm_y': 0.48, 'z': 0.0}
        lms[4] = {'norm_x': 0.5 + 0.12 * thumb_dir, 'norm_y': 0.32, 'z': 0.0} # Far above index MCP
    elif finger_states.get('Thumb', False):
        # Open Thumb: Spread outward to the side
        lms[1] = {'norm_x': 0.5 + 0.12 * thumb_dir, 'norm_y': 0.70, 'z': 0.0}
        lms[2] = {'norm_x': 0.5 + 0.20 * thumb_dir, 'norm_y': 0.62, 'z': 0.0}
        lms[3] = {'norm_x': 0.5 + 0.28 * thumb_dir, 'norm_y': 0.54, 'z': 0.0}
        lms[4] = {'norm_x': 0.5 + 0.36 * thumb_dir, 'norm_y': 0.46, 'z': 0.0}
    else:
        # Folded Thumb: Tucked across the palm (close to pinky MCP)
        lms[1] = {'norm_x': 0.5 + 0.08 * thumb_dir, 'norm_y': 0.70, 'z': 0.0}
        lms[2] = {'norm_x': 0.5 + 0.04 * thumb_dir, 'norm_y': 0.64, 'z': 0.0}
        lms[3] = {'norm_x': 0.5 - 0.02 * thumb_dir, 'norm_y': 0.60, 'z': 0.0}
        lms[4] = {'norm_x': 0.5 - 0.06 * thumb_dir, 'norm_y': 0.58, 'z': 0.0}
        
    return lms


def run_tests():
    print("=" * 60)
    print("      AirControl AI: Automated Gesture Recognition Tests     ")
    print("=" * 60)
    
    engine = GestureEngine(persistence_frames=10)
    controller = YouTubeController()
    controller.toggle_arm()  # ARM controller for testing
    
    # Helper lambda
    def classify_lms(lms):
        f_states, p_scale = engine.analyze_finger_states(lms)
        return engine.classify_raw_gesture(f_states, lms, p_scale)

    # -------------------------------------------------------------
    # Test 1: Closed Fist Classification
    # -------------------------------------------------------------
    fist_lms = generate_hand_landmarks({'Thumb': False, 'Index': False, 'Middle': False, 'Ring': False, 'Pinky': False})
    res = classify_lms(fist_lms)
    print(f"Test 1 [Closed Fist]: Classified as '{res}'")
    assert res == "CLOSED_FIST", f"Expected CLOSED_FIST, got {res}"
    
    # -------------------------------------------------------------
    # Test 2: Open Palm Classification
    # -------------------------------------------------------------
    palm_lms = generate_hand_landmarks({'Thumb': True, 'Index': True, 'Middle': True, 'Ring': True, 'Pinky': True})
    res = classify_lms(palm_lms)
    print(f"Test 2 [Open Palm]: Classified as '{res}'")
    assert res == "OPEN_PALM", f"Expected OPEN_PALM, got {res}"
    
    # -------------------------------------------------------------
    # Test 3: Thumbs Up Classification
    # -------------------------------------------------------------
    thumbs_up_lms = generate_hand_landmarks({'Thumb': True, 'Index': False, 'Middle': False, 'Ring': False, 'Pinky': False}, is_thumbs_up=True)
    res = classify_lms(thumbs_up_lms)
    print(f"Test 3 [Thumbs Up]: Classified as '{res}'")
    assert res == "THUMBS_UP", f"Expected THUMBS_UP, got {res}"
    
    # -------------------------------------------------------------
    # Test 4: Peace Sign Classification
    # -------------------------------------------------------------
    peace_lms = generate_hand_landmarks({'Thumb': False, 'Index': True, 'Middle': True, 'Ring': False, 'Pinky': False})
    res = classify_lms(peace_lms)
    print(f"Test 4 [Peace Sign]: Classified as '{res}'")
    assert res == "PEACE_SIGN", f"Expected PEACE_SIGN, got {res}"
    
    # -------------------------------------------------------------
    # Test 5: Ambiguous / UNKNOWN Poses (Pointing single finger, Rock sign, 3 fingers)
    # -------------------------------------------------------------
    point_lms = generate_hand_landmarks({'Thumb': False, 'Index': True, 'Middle': False, 'Ring': False, 'Pinky': False})
    res_point = classify_lms(point_lms)
    print(f"Test 5a [Single Finger Pointing]: Classified as '{res_point}'")
    assert res_point == "UNKNOWN", f"Expected UNKNOWN for pointing, got {res_point}"
    
    three_lms = generate_hand_landmarks({'Thumb': False, 'Index': True, 'Middle': True, 'Ring': True, 'Pinky': False})
    res_three = classify_lms(three_lms)
    # -------------------------------------------------------------
    # Test 4b: Rock Sign (Next Video) Classification
    # -------------------------------------------------------------
    rock_lms = generate_hand_landmarks({'Thumb': False, 'Index': True, 'Middle': False, 'Ring': False, 'Pinky': True})
    res_rock = classify_lms(rock_lms)
    print(f"Test 4b [Rock Sign]: Classified as '{res_rock}'")
    assert res_rock == "ROCK_SIGN", f"Expected ROCK_SIGN, got {res_rock}"
    
    # -------------------------------------------------------------
    # Test 6: UNKNOWN Never Triggers an Action in Controller
    # -------------------------------------------------------------
    ok, msg = controller.trigger_action("UNKNOWN")
    print(f"Test 6 [UNKNOWN Execution Guard]: Triggered={ok}, Msg='{msg}'")
    assert not ok, "UNKNOWN must never trigger a controller action!"
    assert "UNKNOWN" in msg
    
    # -------------------------------------------------------------
    # Test 7: 10-Frame Persistence Stability
    # -------------------------------------------------------------
    engine_stream = GestureEngine(persistence_frames=10)
    for frame_idx in range(1, 10):
        step_res = engine_stream.process_frame(palm_lms)
        assert step_res['stable_gesture'] == "UNKNOWN", f"Frame {frame_idx} should not trigger yet!"
        assert step_res['is_new_trigger'] == False
    print("Test 7a [Frames 1-9]: Correctly suppressed prior to 10th frame.")
    
    # 10th consecutive frame: Must recognize stable gesture & trigger ONCE
    step_10 = engine_stream.process_frame(palm_lms)
    print(f"Test 7b [Frame 10]: Stable Gesture='{step_10['stable_gesture']}', Triggered={step_10['is_new_trigger']}")
    assert step_10['stable_gesture'] == "OPEN_PALM"
    assert step_10['is_new_trigger'] == True
    
    # -------------------------------------------------------------
    # Test 8: Latch Prevention (Holding gesture for 10 more frames does NOT trigger repeatedly)
    # -------------------------------------------------------------
    for frame_idx in range(11, 21):
        step_hold = engine_stream.process_frame(palm_lms)
        assert step_hold['is_new_trigger'] == False, f"Frame {frame_idx} repeated action while held!"
    print("Test 8 [Holding Latch]: Held Open Palm for 10 frames without any repeated triggers.")
    
    # -------------------------------------------------------------
    # Test 9: Neutral Reset (Returning to neutral allows triggering again)
    # -------------------------------------------------------------
    # Feed 4 neutral frames (NO_HAND or UNKNOWN)
    for _ in range(4):
        engine_stream.process_frame(None)
    assert engine_stream.latched_gesture is None, "Latch should reset after returning to neutral!"
    print("Test 9a [Neutral Reset]: Successfully unlatched after hand returned to neutral.")
    
    # Now feed Closed Fist for 10 frames
    for _ in range(9):
        engine_stream.process_frame(fist_lms)
    step_fist = engine_stream.process_frame(fist_lms)
    print(f"Test 9b [New Gesture after Neutral]: Stable Gesture='{step_fist['stable_gesture']}', Triggered={step_fist['is_new_trigger']}")
    assert step_fist['stable_gesture'] == "CLOSED_FIST"
    assert step_fist['is_new_trigger'] == True
    
    # -------------------------------------------------------------
    # Test 10: Left Hand and Right Hand Invariance
    # -------------------------------------------------------------
    left_fist = generate_hand_landmarks({'Thumb': False, 'Index': False, 'Middle': False, 'Ring': False, 'Pinky': False}, is_left_hand=True)
    res_left_fist = classify_lms(left_fist)
    assert res_left_fist == "CLOSED_FIST"
    
    left_palm = generate_hand_landmarks({'Thumb': True, 'Index': True, 'Middle': True, 'Ring': True, 'Pinky': True}, is_left_hand=True)
    res_left_palm = classify_lms(left_palm)
    assert res_left_palm == "OPEN_PALM"
    print("Test 10 [Left vs Right Hand]: Symmetrical classification confirmed for both hands.")
    
    print("\n" + "=" * 60)
    print("       ALL 10 VERIFICATION TESTS PASSED SUCCESSFULLY!        ")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
