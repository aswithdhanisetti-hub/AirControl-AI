"""Robust Gesture Recognition Engine adhering strictly to the 4 target gestures:
- Closed Fist: Pause (k)
- Open Palm: Play (k)
- Thumbs Up: Volume Up (up)
- Peace Sign: Mute/Unmute (m)
All ambiguous or transitional poses are classified as UNKNOWN (which never triggers actions).
"""
import math
import time
from collections import deque
from typing import List, Dict, Tuple, Optional


class GestureEngine:
    def __init__(self, persistence_frames: int = 10):
        # Frame stability requirement (8-12 frames -> default 10)
        self.persistence_frames = persistence_frames
        self.history = deque(maxlen=persistence_frames)
        
        # Latching control: trigger each action only ONCE per gesture
        # Must return to neutral (UNKNOWN or NO_HAND) or switch gesture to re-arm
        self.latched_gesture: Optional[str] = None
        self.neutral_frames_count: int = 0

    def analyze_finger_states(self, landmarks: List[Dict]) -> Tuple[Dict[str, bool], float]:
        """Analyzes each finger's extension state using hand-relative geometric metrics.
        Returns ({'Thumb': bool, 'Index': bool, 'Middle': bool, 'Ring': bool, 'Pinky': bool}, palm_scale).
        """
        if not landmarks or len(landmarks) < 21:
            return {
                'Thumb': False, 'Index': False, 'Middle': False, 'Ring': False, 'Pinky': False
            }, 1.0

        w0 = landmarks[0]   # Wrist
        m9 = landmarks[9]   # Middle MCP
        
        # Scale reference: Euclidean distance from Wrist to Middle Knuckle
        palm_scale = max(1e-4, math.hypot(w0['norm_x'] - m9['norm_x'], w0['norm_y'] - m9['norm_y']))
        
        # Finger landmark topologies: (MCP, PIP, DIP, TIP)
        finger_topology = {
            'Index': (5, 6, 7, 8),
            'Middle': (9, 10, 11, 12),
            'Ring': (13, 14, 15, 16),
            'Pinky': (17, 18, 19, 20)
        }
        
        finger_states = {}
        for name, (mcp_idx, pip_idx, dip_idx, tip_idx) in finger_topology.items():
            mcp = landmarks[mcp_idx]
            pip = landmarks[pip_idx]
            tip = landmarks[tip_idx]
            
            # Hand-relative Euclidean distances
            d_tip_wrist = math.hypot(tip['norm_x'] - w0['norm_x'], tip['norm_y'] - w0['norm_y'])
            d_pip_wrist = math.hypot(pip['norm_x'] - w0['norm_x'], pip['norm_y'] - w0['norm_y'])
            d_tip_mcp = math.hypot(tip['norm_x'] - mcp['norm_x'], tip['norm_y'] - mcp['norm_y'])
            d_pip_mcp = math.hypot(pip['norm_x'] - mcp['norm_x'], pip['norm_y'] - mcp['norm_y'])
            
            # A finger is OPEN if the tip is farther from both wrist and MCP than the PIP knuckle
            is_extended = (d_tip_wrist > d_pip_wrist * 1.08) and (d_tip_mcp > d_pip_mcp * 1.12)
            finger_states[name] = is_extended
            
        # Thumb Analysis:
        # Landmarks: 0 (Wrist), 1 (CMC), 2 (MCP), 3 (IP), 4 (Tip), 17 (Pinky MCP)
        t4 = landmarks[4]
        p17 = landmarks[17]
        
        # Distance from thumb tip to pinky MCP normalized by palm scale.
        # This is symmetric and invariant for both Left and Right hands (and mirrored feeds)
        d_thumb_pinky = math.hypot(t4['norm_x'] - p17['norm_x'], t4['norm_y'] - p17['norm_y'])
        thumb_span_ratio = d_thumb_pinky / palm_scale
        
        # Thumb is extended when spread outward away from pinky MCP
        thumb_extended = thumb_span_ratio > 1.05
        finger_states['Thumb'] = thumb_extended
        
        return finger_states, palm_scale

    def classify_raw_gesture(self, finger_states: Dict[str, bool], landmarks: List[Dict], palm_scale: float) -> str:
        """Applies distinct rules to recognize the 4 allowed gestures or return UNKNOWN."""
        t = finger_states['Thumb']
        i = finger_states['Index']
        m = finger_states['Middle']
        r = finger_states['Ring']
        p = finger_states['Pinky']
        
        four_fingers_folded = (not i) and (not m) and (not r) and (not p)
        
        t4 = landmarks[4]   # Thumb Tip
        t3 = landmarks[3]   # Thumb IP
        t2 = landmarks[2]   # Thumb MCP
        i5 = landmarks[5]   # Index MCP
        
        # Vertical displacement of thumb joints
        dy_thumb = t2['norm_y'] - t4['norm_y']  # Positive when tip is higher than MCP
        dx_thumb = abs(t4['norm_x'] - t2['norm_x'])
        thumb_segment_len = math.hypot(dx_thumb, dy_thumb)
        
        # Rule 1: Thumbs Up (👍)
        # Thumb extended upward, with the other four fingers folded
        is_thumbs_up = (
            four_fingers_folded and
            (t4['norm_y'] < i5['norm_y'] - 0.16 * palm_scale) and  # Tip well above index knuckle
            (t4['norm_y'] < t3['norm_y'] <= t2['norm_y'] + 0.05 * palm_scale) and  # Joints strictly upward
            (dy_thumb > 0.72 * thumb_segment_len)  # Mostly vertical orientation
        )
        if is_thumbs_up:
            return "THUMBS_UP"
            
        # Rule 2: Closed Fist (✊)
        # Index, middle, ring, and pinky folded (and thumb NOT pointing upward as Thumbs Up)
        if four_fingers_folded:
            return "CLOSED_FIST"
            
        # Rule 3: Open Palm (✋)
        # All five fingers extended
        if t and i and m and r and p:
            return "OPEN_PALM"
            
        # Rule 4: Peace Sign (✌️)
        # Index and middle fingers extended, with ring, pinky, and thumb folded
        if i and m and (not r) and (not p) and (not t):
            d_index_middle = math.hypot(landmarks[8]['norm_x'] - landmarks[12]['norm_x'],
                                        landmarks[8]['norm_y'] - landmarks[12]['norm_y'])
            if d_index_middle > 0.15 * palm_scale:
                return "PEACE_SIGN"
                
        # Rule 5: Rock Sign (🤟 / 🤘) -> NEXT VIDEO
        # Index and Pinky extended, Middle and Ring folded
        if i and p and (not m) and (not r):
            return "ROCK_SIGN"
                
        # Ambiguous or non-matching hand pose
        return "UNKNOWN"

    def process_frame(self, landmarks: Optional[List[Dict]]) -> Dict:
        """Processes frame landmarks, applies 8-12 frame persistence buffer,
        and manages latching so each action triggers only once until neutral reset.
        """
        if not landmarks or len(landmarks) < 21:
            self.history.append("NO_HAND")
            self.neutral_frames_count += 1
            if self.neutral_frames_count >= 3:
                self.latched_gesture = None
                
            return {
                'raw_gesture': "NO_HAND",
                'stable_gesture': "NO_HAND",
                'is_new_trigger': False,
                'finger_states': {'Thumb': False, 'Index': False, 'Middle': False, 'Ring': False, 'Pinky': False},
                'is_latched': False,
                'stability_count': 0
            }

        # 1. Geometric extraction
        finger_states, palm_scale = self.analyze_finger_states(landmarks)
        
        # 2. Raw classification
        raw_gesture = self.classify_raw_gesture(finger_states, landmarks, palm_scale)
        self.history.append(raw_gesture)
        
        # 3. Stability check (8-12 frame persistence, default 10)
        stable_gesture = "UNKNOWN"
        matching_count = self.history.count(raw_gesture)
        
        if len(self.history) == self.persistence_frames:
            # Check if all frames in history match and are not UNKNOWN
            if matching_count == self.persistence_frames and raw_gesture != "UNKNOWN":
                stable_gesture = raw_gesture
                
        # 4. Latching & Trigger Management
        is_new_trigger = False
        allowed_actions = ("CLOSED_FIST", "OPEN_PALM", "THUMBS_UP", "PEACE_SIGN", "ROCK_SIGN")
        
        if stable_gesture in allowed_actions:
            if self.latched_gesture != stable_gesture:
                # Trigger action ONCE upon stabilizing
                is_new_trigger = True
                self.latched_gesture = stable_gesture
                self.neutral_frames_count = 0
        else:
            # When the hand returns to neutral/unknown or releases
            self.neutral_frames_count += 1
            if self.neutral_frames_count >= 4:
                # Reset latch so a future gesture can trigger again
                self.latched_gesture = None

        return {
            'raw_gesture': raw_gesture,
            'stable_gesture': stable_gesture,
            'is_new_trigger': is_new_trigger,
            'finger_states': finger_states,
            'is_latched': (self.latched_gesture is not None),
            'stability_count': matching_count
        }
