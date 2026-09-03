import os

# --- Model & File Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_MODEL_PATH = os.path.join(BASE_DIR, "donghoai_best.pt")
FALLBACK_MODEL_PATH = os.path.join(BASE_DIR, "dongho_best.pt")
KNOWLEDGE_BASE_FILE = os.path.join(BASE_DIR, "knowledge.json")
AUDIO_CACHE_DIR = os.path.join(BASE_DIR, "audio_cache")
TEMP_AUDIO_FILE = os.path.join(BASE_DIR, "temp_speech.mp3")

# Ensure cache directory exists
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

# --- Roboflow Configuration (Fallback) ---
USE_ROBOFLOW_API = False
ROBOFLOW_CFG = {
    "api_key": "dHZzlxGLyNS6lFW1yf46",
    "workspace": "tDH",
    "project": "dongho-tactile-2",
    "version": 4
}

# --- Computer Vision & Tracking Settings ---
CONFIDENCE_THRESHOLD = 0.25
DWELL_TIME_THRESHOLD = 0.8  # Seconds finger must hover over target to trigger
FINGER_SMOOTHING_ALPHA = 0.5  # Exponential Moving Average factor (0=old only, 1=raw)
MAX_HANDS = 1

# --- Voice & AI Q&A Settings ---
# Microsoft Edge-TTS High Quality Natural Voices
TTS_VOICES = {
    "vi": "vi-VN-HoaiMyNeural",     # Giọng nữ tiếng Việt truyền cảm
    "en": "en-US-JennyNeural",       # Natural English
    "zh": "zh-CN-XiaoxiaoNeural"     # Natural Chinese
}

# Gemini API Configuration for Voice Q&A
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# --- Label Mapping ---
LABEL_MAP = {
    "cat": "Majestic_Cat",
    "groom": "Groom_Mouse",
    "bride": "Bride_Mouse",
    "carrying_mice": "Palanquin_Bearer_Mouse",
    "gifts_mice": "Offering_Mouse",
    "servant_mice": "Servant_Mouse",
    "musician_mice": "Musician_Mouse",
    "musician mice": "Musician_Mouse",
    "ho_uy_nghi": "Majestic_Cat",
    "meo_uy_nghi": "Majestic_Cat"
}

# --- Modes & Languages Display ---
AUDIENCE_MODES = {
    "child": "1. Trẻ Em (Child)",
    "elderly": "2. Người Cao Tuổi (Elderly)",
    "blindness": "3. Khiếm Thị (Tactile)",
    "adult": "4. Người Lớn (Adult)"
}

LANGUAGES = {
    "vi": "VI (Tiếng Việt)",
    "en": "EN (English)",
    "zh": "ZH (Chinese)"
}
