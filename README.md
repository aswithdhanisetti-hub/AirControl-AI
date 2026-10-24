# 🖐️ AirControl AI — Hand Gesture YouTube Controller

Control YouTube playback using hand gestures and your laptop webcam! AirControl AI is a Python-based computer vision project that uses MediaPipe to detect hand landmarks and recognize gestures in real time.

The goal is to make video playback more convenient by allowing users to control YouTube without repeatedly reaching for their keyboard or mouse.

## ✨ Features

- 📷 Real-time hand tracking through a webcam.
- 🤖 Hand landmark detection using MediaPipe.
- 🖐️ Recognition of predefined hand gestures.
- ▶️ Gesture-based YouTube playback control.
- 🔊 Volume control using a hand gesture.
- 🔇 Mute and unmute functionality.
- 🛡️ Arm/Disarm safety switch.
- 🎯 Gesture stabilization to reduce accidental triggers.
- 🖥️ Live camera preview with gesture information.
- ⌨️ Keyboard shortcuts for safe operation.

## 🖐️ Supported Gestures

| Hand Gesture | Action | YouTube Shortcut |
|---|---|---|
| ✊ Closed Fist | Pause | `K` |
| ✋ Open Palm | Play | `K` |
| 👍 Thumbs Up | Increase volume | `↑` |
| ✌️ Peace Sign | Mute / Unmute | `M` |

**Note:** Play and pause use the same YouTube keyboard shortcut. The application must correctly identify the gesture before sending the shortcut.

Unsupported or ambiguous gestures should not trigger any action.

## 🛠️ Technologies Used

- **Python** — Application logic
- **OpenCV** — Webcam access and image processing
- **MediaPipe** — Hand landmark detection
- **NumPy** — Numerical and geometric calculations
- **PyAutoGUI** — Keyboard input simulation
- **PyGetWindow** — Active-window inspection
- **Git and GitHub** — Version control and project hosting

## 📂 Project Structure

```text
AirControl-AI/
├── core/
│   ├── controller.py
│   ├── gesture_engine.py
│   └── hand_tracker.py
├── models/
│   └── hand_landmarker.task
├── tests/
│   ├── test_camera.py
│   ├── test_gestures.py
│   └── test_hands.py
├── utils/
│   ├── model_downloader.py
│   └── visualizer.py
├── main.py
├── requirements.txt
├── run.bat
├── .gitignore
└── README.md
```

## 💻 Requirements

- Windows 10 or Windows 11
- Python version compatible with the dependencies in `requirements.txt`
- A working webcam
- Google Chrome or another compatible browser
- An internet connection for downloading dependencies and accessing YouTube

## 🚀 Installation and Setup

### 1. Clone the repository

Open PowerShell and run:

```powershell
git clone https://github.com/aswithdhanisetti-hub/AirControl-AI.git
```

### 2. Open the project directory

```powershell
cd AirControl-AI
```

### 3. Create a virtual environment

```powershell
python -m venv .venv
```

### 4. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 6. Run the application

```powershell
python main.py
```

Alternatively, on Windows, double-click `run.bat` if it is configured to launch the application.

## 🎮 How to Use

1. Start AirControl AI.
2. Open a YouTube video in your browser.
3. Click the video player so it can receive keyboard shortcuts.
4. Focus the AirControl AI camera preview and press `Spacebar` to arm the controls.
5. Show one of the supported gestures to the webcam.
6. Observe the detected gesture and verify that the expected YouTube action occurs.
7. Press `Spacebar` again to disarm the controls when finished.

### Keyboard Controls

| Key | Function |
|---|---|
| `Spacebar` | Arm or disarm gesture controls |
| `Q` | Exit the application |
| `Esc` | Exit the application |

## 🛡️ Safety

- Gesture controls should start in the disarmed state.
- Ambiguous or unsupported gestures should not trigger YouTube actions.
- Gesture stabilization helps reduce accidental commands.
- Active-window checks help prevent commands from being sent to unrelated applications.
- The video player should have keyboard focus before gesture controls are enabled.
- Move the mouse to a screen corner to trigger PyAutoGUI's failsafe if necessary.

**Important:** Active-window checks alone cannot guarantee that the YouTube video player, rather than a search box or comment field, has keyboard focus. Use the arm/disarm control carefully.

## 🧪 Testing

The repository includes test scripts for individual components:

```powershell
python tests/test_camera.py
python tests/test_hands.py
python tests/test_gestures.py
```

Run these scripts individually according to their implementation. A successful test of one component does not necessarily mean the complete application has been tested.

## 📸 Screenshots and Demo

Screenshots and a demonstration video can be added here to show the application running and recognizing gestures.

**Suggested screenshots:**
- Webcam preview with hand landmarks.
- Open palm recognition.
- Thumbs-up recognition.
- Peace sign recognition.
- YouTube playback controlled by a gesture.

## 🎯 Project Goals

AirControl AI explores how computer vision and hand gesture recognition can make human-computer interaction more natural and accessible.

The project also provides practical experience with Python, real-time image processing, landmark-based gesture classification, and application integration.

## 👨‍💻 Author

**Aswith Dhanisetti**

GitHub: [@aswithdhanisetti-hub](https://github.com/aswithdhanisetti-hub)

## 📄 License

No license has been specified yet. A license can be added if you decide how others may use, modify, and distribute this project.