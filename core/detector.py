import os
import cv2
import time
from config import LOCAL_MODEL_PATH, FALLBACK_MODEL_PATH, USE_ROBOFLOW_API, ROBOFLOW_CFG, CONFIDENCE_THRESHOLD, LABEL_MAP

class YOLODetector:
    def __init__(self, use_api=USE_ROBOFLOW_API, local_path=LOCAL_MODEL_PATH, confidence=CONFIDENCE_THRESHOLD):
        self.use_api = use_api
        self.model = None
        self.confidence = confidence
        self.last_detections = []
        self.last_request_time = 0
        self.request_interval = 0.5

        if self.use_api:
            self._init_roboflow()

        if not self.model:
            self._init_local_model(local_path)

    def _init_roboflow(self):
        try:
            from roboflow import Roboflow
            print("[YOLO] Đang kết nối Roboflow API...", flush=True)
            rf = Roboflow(api_key=ROBOFLOW_CFG["api_key"])
            project_rf = rf.workspace(ROBOFLOW_CFG["workspace"]).project(ROBOFLOW_CFG["project"])
            self.model = project_rf.version(ROBOFLOW_CFG["version"]).model
            print("[YOLO] Kết nối Roboflow API thành công!", flush=True)
        except Exception as e:
            print(f"[YOLO] Không thể tải Roboflow API ({e}). Đang chuyển sang model Local...", flush=True)
            self.use_api = False

    def _init_local_model(self, local_path):
        target_path = local_path if os.path.exists(local_path) else FALLBACK_MODEL_PATH
        try:
            from ultralytics import YOLO
            if os.path.exists(target_path):
                print(f"[YOLO] Đang nạp model YOLO local từ: {target_path}", flush=True)
                self.model = YOLO(target_path)
                print("[YOLO] Nạp model YOLO local thành công!", flush=True)
            else:
                print(f"[YOLO] Cảnh báo: Không tìm thấy file weights tại {target_path}", flush=True)
        except Exception as e:
            print(f"[YOLO] Lỗi khởi tạo model local: {e}", flush=True)

    def normalize_class_name(self, raw_name):
        mapped = LABEL_MAP.get(raw_name)
        if mapped:
            return mapped
        # Normalize snake_case or spaces
        clean = raw_name.replace("-", "_").replace(" ", "_").lower()
        return LABEL_MAP.get(clean, raw_name.replace("_", " ").title().replace(" ", "_"))

    def detect(self, frame):
        if self.model is None:
            return []

        if self.use_api:
            return self._detect_api(frame)
        else:
            return self._detect_local(frame)

    def _detect_api(self, frame):
        current_time = time.time()
        if current_time - self.last_request_time < self.request_interval:
            return self.last_detections

        try:
            temp_path = "temp_rf.jpg"
            cv2.imwrite(temp_path, frame)
            predictions = self.model.predict(temp_path, confidence=int(self.confidence * 100), overlap=30).json()
            self.last_request_time = current_time

            detections = []
            for pred in predictions.get('predictions', []):
                cx, cy, w, h = pred['x'], pred['y'], pred['width'], pred['height']
                x1, y1 = int(cx - w / 2), int(cy - h / 2)
                x2, y2 = int(cx + w / 2), int(cy + h / 2)
                class_name = self.normalize_class_name(pred['class'])

                detections.append({
                    "class": class_name,
                    "bbox": [x1, y1, x2, y2],
                    "conf": float(pred['confidence'])
                })

            self.last_detections = detections
            return detections
        except Exception as e:
            print(f"[YOLO] API inference error: {e}", flush=True)
            return self.last_detections

    def _detect_local(self, frame):
        try:
            results = self.model.predict(frame, conf=self.confidence, verbose=False)
            detections = []
            for result in results:
                for box in result.boxes:
                    coords = box.xyxy[0].cpu().numpy()
                    cls_id = int(box.cls[0])
                    raw_name = self.model.names[cls_id]
                    class_name = self.normalize_class_name(raw_name)

                    detections.append({
                        "class": class_name,
                        "bbox": coords,
                        "conf": float(box.conf[0])
                    })
            return detections
        except Exception as e:
            print(f"[YOLO] Local inference error: {e}", flush=True)
            return []
