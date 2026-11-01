import os

# --- Model & File Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_MODEL_PATH = os.path.join(BASE_DIR, "donghoai_best.pt")
FALLBACK_MODEL_PATH = os.path.join(BASE_DIR, "dongho_best.pt")
KNOWLEDGE_BASE_FILE = os.path.join(BASE_DIR, "knowledge.json")
AUDIO_CACHE_DIR = os.path.join(BASE_DIR, "audio_cache")
TEMP_AUDIO_FILE = os.path.join(BASE_DIR, "temp_speech.mp3")

# --- MediaPipe Hand Landmarker (Tasks API) ---
# Lưu ý: bản mediapipe đang cài chỉ cung cấp Tasks API (không có mp.solutions),
# nên cần file model .task cho HandLandmarker.
MEDIAPIPE_HAND_MODEL_PATH = os.path.join(BASE_DIR, "hand_landmarker.task")
MEDIAPIPE_HAND_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)

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
# Model được train lại 150 epochs (mAP50 ~0.98). Ngưỡng 0.20 cân bằng giữa
# việc bắt đủ nhân vật qua webcam và hạn chế box nhiễu.
CONFIDENCE_THRESHOLD = 0.20
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
    "meo_uy_nghi": "Majestic_Cat",
    # Nhãn tiếng Việt của model fallback (dongho_best.pt)
    "chuot_chu_re": "Groom_Mouse",
    "chuot_co_dau": "Bride_Mouse",
    "chuot_khenh_kieu": "Palanquin_Bearer_Mouse",
    "chuot_mang_le_vat": "Offering_Mouse",
    "chuot_nguoi_hau": "Servant_Mouse",
    "chuot_nhac_cong": "Musician_Mouse"
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
