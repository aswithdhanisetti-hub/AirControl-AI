"""Core Hand Tracker using MediaPipe Tasks Vision API."""
import os
import time
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from utils.model_downloader import ensure_model_downloaded

# Standard MediaPipe 21 hand landmark connections
HAND_CONNECTIONS = [
    # Thumb
    (0, 1), (1, 2), (2, 3), (3, 4),
    # Index finger
    (0, 5), (5, 6), (6, 7), (7, 8),
    # Middle finger
    (9, 10), (10, 11), (11, 12),
    # Ring finger
    (13, 14), (14, 15), (15, 16),
    # Pinky
    (0, 17), (17, 18), (18, 19), (19, 20),
    # Palm knuckles
    (5, 9), (9, 13), (13, 17)
]


class HandTracker:
    def __init__(self, num_hands: int = 1, min_detection_confidence: float = 0.5):
        """Initializes MediaPipe Tasks HandLandmarker."""
        model_path = ensure_model_downloaded()
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_detection_confidence,
            min_tracking_confidence=min_detection_confidence
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self.last_result = None

    def find_hands(self, frame_bgr: np.ndarray):
        """Processes a BGR image frame and extracts hand landmarks.
        Returns the raw HandLandmarkerResult.
        """
        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        self.last_result = self.landmarker.detect(mp_image)
        return self.last_result

    def get_hand_landmarks(self, frame_shape, hand_index: int = 0):
        """Returns pixel coordinates for the specified hand as a list of dicts:
        [{'id': 0, 'x': px, 'y': py, 'z': norm_z, 'norm_x': x, 'norm_y': y}, ...]
        Returns None if no hand detected.
        """
        if not self.last_result or not self.last_result.hand_landmarks:
            return None
        if hand_index >= len(self.last_result.hand_landmarks):
            return None
            
        h, w = frame_shape[:2]
        raw_landmarks = self.last_result.hand_landmarks[hand_index]
        landmarks = []
        for idx, lm in enumerate(raw_landmarks):
            px_x = int(lm.x * w)
            px_y = int(lm.y * h)
            landmarks.append({
                'id': idx,
                'x': px_x,
                'y': px_y,
                'z': lm.z,
                'norm_x': lm.x,
                'norm_y': lm.y
            })
        return landmarks

    def get_handedness(self, hand_index: int = 0):
        """Returns handedness string ('Left' or 'Right') and confidence score."""
        if not self.last_result or not self.last_result.handedness:
            return None, 0.0
        if hand_index >= len(self.last_result.handedness):
            return None, 0.0
        cat = self.last_result.handedness[hand_index][0]
        # category_name or display_name
        name = cat.category_name if cat.category_name else cat.display_name
        return name, cat.score

    def draw_landmarks(self, frame_bgr: np.ndarray, landmarks, color=(0, 255, 128), line_color=(0, 180, 255)):
        """Draws aesthetic hand skeleton joints and connection bones on the frame."""
        if not landmarks:
            return frame_bgr
            
        # Draw bones
        for start_idx, end_idx in HAND_CONNECTIONS:
            p1 = (landmarks[start_idx]['x'], landmarks[start_idx]['y'])
            p2 = (landmarks[end_idx]['x'], landmarks[end_idx]['y'])
            cv2.line(frame_bgr, p1, p2, line_color, 2, cv2.LINE_AA)
            
        # Draw joints
        for lm in landmarks:
            pt = (lm['x'], lm['y'])
            # Fingertips (4, 8, 12, 16, 20) get slightly larger highlight
            is_tip = lm['id'] in (4, 8, 12, 16, 20)
            radius = 6 if is_tip else 4
            dot_color = (0, 120, 255) if is_tip else color
            cv2.circle(frame_bgr, pt, radius, dot_color, -1, cv2.LINE_AA)
            cv2.circle(frame_bgr, pt, radius + 1, (255, 255, 255), 1, cv2.LINE_AA)
            
        return frame_bgr
