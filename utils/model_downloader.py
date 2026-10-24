"""Model downloader utility for MediaPipe Tasks Hand Landmarker."""
import os
import urllib.request
import sys

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
MODEL_FILENAME = "hand_landmarker.task"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
MIN_EXPECTED_BYTES = 5_000_000  # Expected size ~7.8 MB


def ensure_model_downloaded() -> str:
    """Checks if hand_landmarker.task exists and is valid; downloads it if missing."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    if os.path.exists(MODEL_PATH):
        file_size = os.path.getsize(MODEL_PATH)
        if file_size >= MIN_EXPECTED_BYTES:
            print(f"[ModelDownloader] Model found at {MODEL_PATH} ({file_size / (1024*1024):.2f} MB)")
            return MODEL_PATH
        else:
            print(f"[ModelDownloader] Incomplete model found ({file_size} bytes). Re-downloading...")
            os.remove(MODEL_PATH)
            
    print(f"[ModelDownloader] Downloading {MODEL_FILENAME} from Google Cloud...")
    print(f"URL: {MODEL_URL}")
    
    def progress_callback(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, int((downloaded / total_size) * 100))
            sys.stdout.write(f"\rDownloading model: {percent}% ({downloaded / (1024*1024):.1f} / {total_size / (1024*1024):.1f} MB)")
            sys.stdout.flush()
            
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH, reporthook=progress_callback)
    print("\n[ModelDownloader] Download complete!")
    
    file_size = os.path.getsize(MODEL_PATH)
    if file_size < MIN_EXPECTED_BYTES:
        raise RuntimeError(f"Downloaded model file is corrupted or too small: {file_size} bytes")
        
    print(f"[ModelDownloader] Model successfully verified: {file_size / (1024*1024):.2f} MB")
    return MODEL_PATH


if __name__ == "__main__":
    ensure_model_downloaded()
