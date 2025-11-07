import cv2
import numpy as np

def draw_boxes(frame, objects, detections):
    """Draw bounding boxes and IDs"""
    
    for det in detections:
        x1, y1, x2, y2, conf = map(int, det[:5])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 2)
        cv2.putText(
            frame, f"{conf:.2f}",
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2
        )
    
    
    for objectID, centroid in objects.items():
        
        centroid_tuple = tuple(map(int, centroid))
        cv2.circle(frame, centroid_tuple, 4, (0, 255, 0), -1)
        cv2.putText(
            frame, f"ID:{objectID}",
            (centroid_tuple[0] - 10, centroid_tuple[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
        )
    
    return frame

def draw_counts(frame, entries, exits, line_y):
    """Draw entry/exit counts and line"""
    h, w = frame.shape[:2]
    
    
    cv2.line(frame, (0, line_y), (w, line_y), (0, 255, 0), 2)
    cv2.putText(frame, "Counting Line", (10, line_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    
    cv2.putText(frame, f"ENTRIES: {entries}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"EXITS: {exits}", (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    net = entries - exits
    color = (0, 255, 0) if net >= 0 else (0, 0, 255)

                
    
    return frame

def draw_fps(frame, fps):
    """Draw FPS counter"""
    cv2.putText(frame, f"FPS: {fps:.1f}", (frame.shape[1] - 150, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return frame
