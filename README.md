# AirControl AI — Hand Gesture YouTube Controller

AirControl AI is a real-time computer vision application that detects hand gestures through your laptop webcam and controls YouTube video playback without requiring keyboard or mouse interactions.

---

## Quick Start (How to Run)

Open PowerShell in this directory (`c:\Users\prana\OneDrive\Desktop\aircontrol`) and run:

```powershell
# Run the complete application
.\.venv\Scripts\python.exe main.py
```
*(Or simply double-click `run.bat` in File Explorer).*

---

## Keyboard Controls in Preview Window

| Key | Action |
| :---: | :--- |
| **`Spacebar`** | **ARM / DISARM Safety Clutch**: Toggles keyboard control on (Green) or off (Amber). |
| **`q`** or **`Esc`** / **`[X]`** | **Exit Cleanly**: Releases webcam hardware and closes preview window. |

---

## 🖐️ Exact Gesture Vocabulary & YouTube Mapping

| Gesture | Finger Extension Rule | YouTube Action | Hotkey |
| :--- | :--- | :---: | :---: |
| ✊ **Closed Fist** | Index, Middle, Ring, Pinky folded | **PAUSE** ⏸ | `'k'` |
| ✋ **Open Palm** | All 5 fingers extended | **PLAY** ▶ | `'k'` |
| 👍 **Thumbs Up** | Thumb extended UP, other 4 fingers folded | **VOLUME UP (+5%)** 🔊 | `Up Arrow` |
| ✌️ **Peace Sign** | Index & Middle extended, Ring & Pinky folded | **MUTE / UNMUTE** 🔇 / 🔊 | `'m'` |
| 🤟 **Rock Sign** | Index & Pinky extended, Middle & Ring folded | **NEXT VIDEO** ⏭ | `Shift + N` |
| ❓ **UNKNOWN** | Any other ambiguous hand pose | **NO ACTION** (Suppressed) | *None* |

---

## 🛡️ Stability & Latching Architecture

1. **8–12 Frame Persistence (10 Frames Default)**: A gesture must remain identical for 10 consecutive video frames before it is accepted as stable.
2. **Single-Trigger Latching**: Once an action is triggered, it will **never repeat** while the gesture is held. The hand must return to neutral (`UNKNOWN` or lower hand) before another action can trigger.
3. **Live Finger Debugging Panel**: The camera window displays the real-time state of each finger (`Thu:OPEN/FOLDED`, `Ind:OPEN/FOLDED`, `Mid:OPEN/FOLDED`, `Rin:OPEN/FOLDED`, `Pin:OPEN/FOLDED`).

---

## Safety Architecture: Active Window Protection

1. **Safety Clutch**: The app boots in `DISARMED` state. No hotkeys are sent until you press `Spacebar`.
2. **Window Check**: Simulated hotkeys are **only** sent when the active window title contains `"- YouTube"`. If you switch to another window, all keystrokes are automatically blocked.
3. **PyAutoGUI Failsafe**: Slamming the mouse cursor into any corner of the screen immediately aborts script execution.

---

## Project Structure

```
aircontrol/
├── .venv/                      # Python virtual environment
├── models/
│   └── hand_landmarker.task    # Google MediaPipe Tasks 21-landmark model (~7.5 MB)
├── core/
│   ├── hand_tracker.py         # MediaPipe Tasks HandLandmarker wrapper & skeleton drawer
│   ├── gesture_engine.py       # Biomechanical classifier, thumb span ratio & latching
│   └── controller.py           # PyAutoGUI hotkeys, Arm switch & active window protection
├── utils/
│   ├── model_downloader.py     # Auto-downloads and verifies model file
│   └── visualizer.py           # Cyber-aesthetic HUD overlay (FPS, flags, status)
├── tests/
│   ├── test_camera.py          # Standalone Step 1 webcam test
│   └── test_hands.py           # Standalone Step 2 hand tracking test
├── requirements.txt            # Dependency configuration
├── main.py                     # Main application entry point
├── run.bat                     # 1-click Windows launcher
└── README.md                   # Documentation
```
