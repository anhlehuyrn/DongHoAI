import os
import time
import urllib.request
import cv2

from config import (
    DWELL_TIME_THRESHOLD,
    FINGER_SMOOTHING_ALPHA,
    MAX_HANDS,
    MEDIAPIPE_HAND_MODEL_PATH,
    MEDIAPIPE_HAND_MODEL_URL,
)


class HandTracker:
    """
    Bám vết đầu ngón tay trỏ bằng MediaPipe Hand Landmarker (Tasks API).

    Lưu ý: bản mediapipe >= 0.10.3x chỉ còn Tasks API (không có mp.solutions),
    nên phải dùng HandLandmarker + file model hand_landmarker.task.
    """

    def __init__(self, max_hands=MAX_HANDS, detection_con=0.7, track_con=0.5):
        self.landmarker = None
        self.mp = None
        self.connections = None

        # Exponential Moving Average for smoothing fingertip
        self.smooth_x = None
        self.smooth_y = None
        self.alpha = FINGER_SMOOTHING_ALPHA

        # Dwell-time state tracking
        self.current_hover_class = None
        self.hover_start_time = None
        self.dwell_threshold = DWELL_TIME_THRESHOLD
        self.has_triggered = False

        self._last_timestamp_ms = 0

        self._init_mediapipe(max_hands, detection_con, track_con)

    def _ensure_model_file(self):
        """Tải file hand_landmarker.task nếu chưa có (chỉ chạy 1 lần)."""
        if os.path.exists(MEDIAPIPE_HAND_MODEL_PATH):
            return True
        try:
            print("[HandTracker] Đang tải model hand_landmarker.task (~7.8MB)...", flush=True)
            urllib.request.urlretrieve(MEDIAPIPE_HAND_MODEL_URL, MEDIAPIPE_HAND_MODEL_PATH)
            print("[HandTracker] Tải model Hand Landmarker thành công!", flush=True)
            return True
        except Exception as e:
            print(f"[HandTracker] Không tải được model Hand Landmarker: {e}", flush=True)
            return False

    def _init_mediapipe(self, max_hands, detection_con, track_con):
        try:
            import mediapipe as mp
            from mediapipe.tasks.python.core.base_options import BaseOptions
            from mediapipe.tasks.python.vision import (
                HandLandmarker,
                HandLandmarkerOptions,
                HandLandmarksConnections,
                RunningMode,
            )

            if not self._ensure_model_file():
                return

            options = HandLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=MEDIAPIPE_HAND_MODEL_PATH),
                running_mode=RunningMode.VIDEO,
                num_hands=max_hands,
                min_hand_detection_confidence=detection_con,
                min_hand_presence_confidence=detection_con,
                min_tracking_confidence=track_con,
            )

            self.mp = mp
            self.landmarker = HandLandmarker.create_from_options(options)
            self.connections = HandLandmarksConnections.HAND_CONNECTIONS
            print("[HandTracker] Khởi tạo MediaPipe Hand Tracking thành công!", flush=True)
        except Exception as e:
            print(f"[HandTracker] Cảnh báo MediaPipe chưa sẵn sàng: {e}", flush=True)

    def find_fingertip(self, frame):
        if self.landmarker is None:
            return None, None

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=img_rgb)

        # Timestamp phải tăng đơn điệu khi dùng RunningMode.VIDEO
        timestamp_ms = max(int(time.time() * 1000), self._last_timestamp_ms + 1)
        self._last_timestamp_ms = timestamp_ms

        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        if result.hand_landmarks:
            hand_lms = result.hand_landmarks[0]
            # Landmark 8: INDEX_FINGER_TIP
            landmark = hand_lms[8]
            h, w, _ = frame.shape
            raw_x, raw_y = int(landmark.x * w), int(landmark.y * h)

            # Smooth coordinates using EMA
            if self.smooth_x is None or self.smooth_y is None:
                self.smooth_x = raw_x
                self.smooth_y = raw_y
            else:
                self.smooth_x = int(self.alpha * raw_x + (1 - self.alpha) * self.smooth_x)
                self.smooth_y = int(self.alpha * raw_y + (1 - self.alpha) * self.smooth_y)

            return (self.smooth_x, self.smooth_y), hand_lms

        # Reset smooth cache when hand is lost
        self.smooth_x = None
        self.smooth_y = None
        return None, None

    def draw_skeleton(self, frame, hand_landmarks):
        """Vẽ xương bàn tay bằng OpenCV từ danh sách landmark."""
        if hand_landmarks is None or self.connections is None:
            return

        h, w, _ = frame.shape
        points = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]

        for conn in self.connections:
            cv2.line(frame, points[conn.start], points[conn.end], (0, 230, 115), 2)
        for point in points:
            cv2.circle(frame, point, 3, (255, 255, 255), -1)

    def update_dwell_touch(self, fingertip, detections):
        """
        Calculates dwell time when finger hovers over a bounding box.
        Returns:
            hover_class: class name of hovered object or None
            progress: float between 0.0 and 1.0 (1.0 = triggered)
            triggered: bool (True only once upon reaching 1.0)
            target_bbox: the bbox currently hovered or None
        """
        if fingertip is None or not detections:
            self._reset_hover()
            return None, 0.0, False, None

        fx, fy = fingertip
        hovered_det = None

        # Check if fingertip is inside any bbox
        for det in detections:
            x1, y1, x2, y2 = map(int, det['bbox'])
            if x1 <= fx <= x2 and y1 <= fy <= y2:
                hovered_det = det
                break

        if hovered_det is None:
            self._reset_hover()
            return None, 0.0, False, None

        class_name = hovered_det['class']
        current_time = time.time()

        if self.current_hover_class != class_name:
            # Started hovering over a new target
            self.current_hover_class = class_name
            self.hover_start_time = current_time
            self.has_triggered = False
            return class_name, 0.0, False, hovered_det['bbox']

        # Continuing hover on same target
        elapsed = current_time - self.hover_start_time
        progress = min(1.0, elapsed / self.dwell_threshold)

        triggered = False
        if progress >= 1.0 and not self.has_triggered:
            triggered = True
            self.has_triggered = True

        return class_name, progress, triggered, hovered_det['bbox']

    def _reset_hover(self):
        self.current_hover_class = None
        self.hover_start_time = None
        self.has_triggered = False
