import cv2
import numpy as np
from typing import Tuple, Optional

class VisionEngine:
    def __init__(self, source=0, weights_path: str = "yolov8n.pt", target_classes=None):
        self.source = source
        self.weights_path = weights_path
        self.target_classes = target_classes or ["cup", "person", "bottle"]
        self.model = None
        self._init_yolo()
        self.cap = None
        self._init_camera()

    def _init_yolo(self):
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.weights_path)
        except Exception:
            self.model = None

    def _init_camera(self):
        try:
            self.cap = cv2.VideoCapture(self.source)
        except Exception:
            self.cap = None

    def get_frame(self) -> Optional[np.ndarray]:
        if self.cap is None or not self.cap.isOpened():
            return None
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def find_laser_center(self, frame: np.ndarray) -> Tuple[int, int]:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_green = np.array([35, 40, 140])
        upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        mask = cv2.dilate(mask, None, iterations=2)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            m = cv2.moments(largest)
            if m["m00"] != 0:
                cx = int(m["m10"] / m["m00"])
                cy = int(m["m01"] / m["m00"])
                return cx, cy
        return -1, -1

    def find_target(self, frame: np.ndarray) -> Tuple[int, int, int, int, bool, bool, Optional[str]]:
        laser_x, laser_y = self.find_laser_center(frame)
        laser_found = (laser_x != -1 and laser_y != -1)
        
        target_x, target_y = -1, -1
        target_found = False
        target_name = None
        
        if self.model is not None:
            results = self.model.predict(frame, imgsz=320, verbose=False, conf=0.25)
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                name = self.model.names[cls_id]
                if name in self.target_classes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    target_x = int((x1 + x2) / 2)
                    target_y = int((y1 + y2) / 2)
                    target_found = True
                    target_name = name
                    break
                    
        return laser_x, laser_y, target_x, target_y, laser_found, target_found, target_name

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
