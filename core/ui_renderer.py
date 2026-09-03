import cv2
import numpy as np

# Color Palette (BGR)
COLOR_BG_DARK = (20, 20, 20)
COLOR_PRIMARY_GREEN = (0, 230, 115)
COLOR_ALERT_RED = (50, 50, 240)
COLOR_HIGHLIGHT_GOLD = (0, 215, 255)
COLOR_ACCENT_BLUE = (255, 178, 50)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (160, 160, 160)

class UIRenderer:
    @staticmethod
    def draw_hud(frame, audience_mode, current_lang, voice_state, fps=0):
        h, w, _ = frame.shape
        
        # --- Top Banner Header ---
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 55), COLOR_BG_DARK, -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        # Title
        cv2.putText(frame, "DongHo.AI - Tactile Heritage Guide", (15, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLOR_HIGHLIGHT_GOLD, 2)
        
        # Status Badges
        status_text = f"Mode: {audience_mode.upper()}  |  Lang: {current_lang.upper()}  |  FPS: {int(fps)}"
        cv2.putText(frame, status_text, (15, 47),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_WHITE, 1)

        # Keyboard Guide on top right
        guide_text = "[1-4]: Mode | [V,E,Z]: Lang | [SPACE]: Voice Ask | [Q]: Quit"
        cv2.putText(frame, guide_text, (w - 480, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, COLOR_GRAY, 1)

        # --- Voice Assistant State Banner (Bottom) ---
        UIRenderer.draw_voice_status(frame, voice_state, w, h)

    @staticmethod
    def draw_voice_status(frame, voice_state, w, h):
        banner_h = 40
        y1 = h - banner_h - 10
        y2 = h - 10
        x1 = 20
        x2 = w - 20

        overlay = frame.copy()
        
        state_color = COLOR_BG_DARK
        state_msg = " [SPACE] Nhan phim SPACE de hoi dap Voice AI voi Gemini"

        if voice_state == "LISTENING":
            state_color = (0, 100, 255)  # Orange
            state_msg = " >>> DANG LANG NGHE GIONG NOI CUA BAN... <<<"
        elif voice_state == "THINKING":
            state_color = (180, 50, 200)  # Purple
            state_msg = " ... AI DANG SUY NGHI & TIM HIEL VE TRANH DONG HO ... "
        elif voice_state == "SPEAKING":
            state_color = (0, 180, 0)  # Green
            state_msg = " ((( AI DANG THUYET MINH )))"

        cv2.rectangle(overlay, (x1, y1), (x2, y2), state_color, -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_WHITE, 1)

        cv2.putText(frame, state_msg, (x1 + 15, y1 + 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, COLOR_WHITE, 2)

    @staticmethod
    def draw_detection(frame, bbox, class_name, is_hovered=False, is_triggered=False):
        x1, y1, x2, y2 = map(int, bbox)
        
        box_color = COLOR_PRIMARY_GREEN
        thickness = 2

        if is_triggered:
            box_color = COLOR_ALERT_RED
            thickness = 3
        elif is_hovered:
            box_color = COLOR_HIGHLIGHT_GOLD
            thickness = 2

        # Draw rounded or standard rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, thickness)
        
        # Label tag background
        label_size, _ = cv2.getTextSize(class_name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        label_w, label_h = label_size
        cv2.rectangle(frame, (x1, y1 - label_h - 10), (x1 + label_w + 10, y1), box_color, -1)
        cv2.putText(frame, class_name, (x1 + 5, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    @staticmethod
    def draw_dwell_ring(frame, fingertip, progress, triggered=False):
        """Vẽ vòng tròn tiến trình (Dwell Progress Ring) quanh đầu ngón tay"""
        if fingertip is None:
            return

        cx, cy = fingertip
        radius = 22
        
        # Center fingertip dot
        cv2.circle(frame, (cx, cy), 6, COLOR_HIGHLIGHT_GOLD, -1)
        cv2.circle(frame, (cx, cy), 8, COLOR_WHITE, 1)

        if progress > 0.0:
            # Background guide ring
            cv2.circle(frame, (cx, cy), radius, (80, 80, 80), 2)
            
            # Progress arc (0 to 360 deg)
            end_angle = int(progress * 360)
            arc_color = COLOR_PRIMARY_GREEN if not triggered else COLOR_ALERT_RED
            cv2.ellipse(frame, (cx, cy), (radius, radius), -90, 0, end_angle, arc_color, 4)
