import cv2
import numpy as np
from ultralytics import YOLO
from config import YOLO_MODEL, DETECTION_CONFIDENCE, NMS_THRESHOLD

class YOLODetector:
    def __init__(self, model_path=YOLO_MODEL):
        """Initialize YOLO model"""
        self.model = YOLO(model_path)
        self.conf_threshold = DETECTION_CONFIDENCE
        self.nms_threshold = NMS_THRESHOLD
    
    def detect(self, frame):
        """
        Detect people in frame
        Returns: list of [x1, y1, x2, y2, confidence]
        """
        results = self.model(frame, conf=self.conf_threshold, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                
                if int(box.cls) == 0:
                    
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    conf = float(box.conf)
                    detections.append([x1, y1, x2, y2, conf])
        
        return np.array(detections) if detections else np.empty((0, 5))
