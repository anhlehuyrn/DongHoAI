import cv2
import json
import time
import os
import sys

# Force UTF-8 stdout for Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from config import (
    KNOWLEDGE_BASE_FILE,
    AUDIENCE_MODES,
    LANGUAGES
)
from core.detector import YOLODetector
from core.hand_tracker import HandTracker
from core.audio_manager import AudioManager
from core.voice_assistant import VoiceAssistant
from core.ui_renderer import UIRenderer

def load_knowledge_base():
    try:
        with open(KNOWLEDGE_BASE_FILE, 'r', encoding='utf-8') as f:
            kb = json.load(f)
            print(f"[Main] Đã tải thành công cơ sở tri thức ({len(kb)} nhân vật).", flush=True)
            return kb
    except Exception as e:
        print(f"[Main] Lỗi tải {KNOWLEDGE_BASE_FILE}: {e}", flush=True)
        return {}

def main():
    print("=========================================================")
    print("   DONGHO.AI - TRỢ LÝ DI SẢN XÚC GIÁC & HỎI ĐÁP AI      ")
    print("=========================================================", flush=True)

    # State
    audience_mode = "blindness"  # Modes: child, elderly, blindness, adult
    current_lang = "vi"          # Languages: vi, en, zh

    # Load Knowledge Base
    knowledge_base = load_knowledge_base()

    # Initialize Modules
    detector = YOLODetector()
    tracker = HandTracker()
    audio_manager = AudioManager()
    voice_assistant = VoiceAssistant(audio_manager=audio_manager, knowledge_base=knowledge_base)

    # Initialize Camera
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[Lỗi] Không thể kết nối với Webcam máy tính.", flush=True)
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("\n[Hệ thống đã sẵn sàng!]", flush=True)
    print(" - Chạm ngón tay và giữ 0.8s vào nhân vật để nghe thuyết minh.")
    print(" - Nhấn phím SPACE để trò chuyện/hỏi đáp giọng nói với AI.")
    print(" - Phím 1,2,3,4: Đổi lứa tuổi | Phím V,E,Z: Đổi ngôn ngữ | Phím Q: Thoát.\n", flush=True)

    prev_time = time.time()
    fps = 30.0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        curr_time = time.time()
        fps = 0.9 * fps + 0.1 * (1.0 / max(0.001, curr_time - prev_time))
        prev_time = curr_time

        # 1. Computer Vision Inferences
        detections = detector.detect(frame)
        fingertip, hand_landmarks = tracker.find_fingertip(frame)

        # 2. Dwell-Time Touch Checking
        hover_class, dwell_progress, is_triggered, hovered_bbox = tracker.update_dwell_touch(fingertip, detections)

        # 3. Handle Touch Event
        if is_triggered and hover_class:
            print(f"[Tương tác] Phát hiện ngón tay giữ vào: {hover_class}", flush=True)
            voice_assistant.set_context(hover_class, audience_mode, current_lang)

            if hover_class in knowledge_base:
                desc_data = knowledge_base[hover_class].get(audience_mode, {})
                text_desc = desc_data.get(current_lang, "") if isinstance(desc_data, dict) else desc_data
                
                # Play audio (pre-cached or generated)
                audio_manager.play_character_description(
                    class_name=hover_class,
                    mode=audience_mode,
                    lang=current_lang,
                    text=text_desc
                )

        # 4. Render Detections
        for det in detections:
            c_name = det['class']
            is_cur_hovered = (hover_class == c_name)
            is_cur_triggered = (is_cur_hovered and dwell_progress >= 1.0)
            UIRenderer.draw_detection(frame, det['bbox'], c_name, is_cur_hovered, is_cur_triggered)

        # 5. Render Hand Landmarks & Dwell Progress Ring
        if hand_landmarks:
            tracker.draw_skeleton(frame, hand_landmarks)
        
        if fingertip:
            UIRenderer.draw_dwell_ring(frame, fingertip, dwell_progress, triggered=(dwell_progress >= 1.0))

        # 6. Render HUD and Status Banners
        UIRenderer.draw_hud(frame, audience_mode, current_lang, voice_assistant.state, fps)

        # 7. Display Window
        cv2.imshow("DongHo.AI - Multimodal Heritage Interface", frame)

        # 8. User Key Controls
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('1'):
            audience_mode = "child"
            voice_assistant.set_context(hover_class, audience_mode, current_lang)
        elif key == ord('2'):
            audience_mode = "elderly"
            voice_assistant.set_context(hover_class, audience_mode, current_lang)
        elif key == ord('3'):
            audience_mode = "blindness"
            voice_assistant.set_context(hover_class, audience_mode, current_lang)
        elif key == ord('4'):
            audience_mode = "adult"
            voice_assistant.set_context(hover_class, audience_mode, current_lang)
        elif key == ord('v'):
            current_lang = "vi"
            voice_assistant.set_context(hover_class, audience_mode, current_lang)
        elif key == ord('e'):
            current_lang = "en"
            voice_assistant.set_context(hover_class, audience_mode, current_lang)
        elif key == ord('z'):
            current_lang = "zh"
            voice_assistant.set_context(hover_class, audience_mode, current_lang)
        elif key == 32:  # SPACE BAR
            # Trigger Voice Assistant Q&A
            if voice_assistant.state == "IDLE":
                voice_assistant.set_context(hover_class or "Bức tranh Đám cưới chuột", audience_mode, current_lang)
                voice_assistant.start_listening_async()

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    audio_manager.stop()
    print("[Main] Đã đóng ứng dụng DongHo.AI an toàn.", flush=True)

if __name__ == "__main__":
    main()