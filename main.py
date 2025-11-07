import cv2
import json
import logging
from datetime import datetime
from pathlib import Path

from config import *
from models.yolo_detector import YOLODetector
from utils.centroid_tracker import CentroidTracker
from utils.line_crossing import LineCrossing
from utils.visualizer import draw_boxes, draw_counts, draw_fps


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FootfallCounter:
    def __init__(self, video_path=None):
        self.detector = YOLODetector()
        self.tracker = CentroidTracker(
            maxDisappeared=MAX_DISAPPEARED_FRAMES,
            maxDistance=MAX_CENTROID_DISTANCE
        )
        self.line_crossing = None
        self.video_path = video_path
        self.frame_count = 0
        self.fps_counter = 0
        
        logger.info("FootfallCounter initialized")
    
    def process_video(self, video_path, output_path=None):
        """Process video and count people"""
        self.video_path = video_path
        
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            logger.error(f"Cannot open video: {video_path}")
            return False
        
        
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        
        self.line_crossing = LineCrossing(frame_height, LINE_POSITION)
        
        
        if output_path is None:
            output_path = OUTPUTS_DIR / "output_video.mp4"
        
        fourcc = cv2.VideoWriter_fourcc(*OUTPUT_CODEC.upper())
        out = cv2.VideoWriter(
            str(output_path),
            fourcc,
            OUTPUT_FPS,
            (frame_width, frame_height)
        )
        
        logger.info(f"Processing video: {video_path}")
        logger.info(f"Resolution: {frame_width}x{frame_height}, FPS: {fps}")
        
        frame_count = 0
        fps_start_time = cv2.getTickCount()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            
            detections = self.detector.detect(frame)
            
            
            objects = self.tracker.update(detections)
            
            
            for objectID, centroid in objects.items():
                history = self.tracker.centroids_history[objectID]
                self.line_crossing.update_counts(objectID, history)
            
            
            frame = draw_boxes(frame, objects, detections)
            frame = draw_counts(
                frame,
                self.line_crossing.entry_count,
                self.line_crossing.exit_count,
                self.line_crossing.line_y
            )
            
            
            if frame_count % FPS_DISPLAY_INTERVAL == 0:
                elapsed = (cv2.getTickCount() - fps_start_time) / cv2.getTickFrequency()
                fps = FPS_DISPLAY_INTERVAL / elapsed
                fps_start_time = cv2.getTickCount()
                frame = draw_fps(frame, fps)
            
            
            out.write(frame)
            
            
            if SHOW_FRAME:
                display_frame = cv2.resize(frame, FRAME_DISPLAY_SIZE)
                cv2.imshow('Footfall Counter', display_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            
            if frame_count % 30 == 0:
                progress = (frame_count / total_frames) * 100
                logger.info(
                    f"Progress: {progress:.1f}% | "
                    f"IN: {self.line_crossing.entry_count} | "
                    f"OUT: {self.line_crossing.exit_count}"
                )
        
        
        cap.release()
        out.release()
        if SHOW_FRAME:
            cv2.destroyAllWindows()
        
        
        self.save_statistics(output_path)
        
        logger.info(f"Processing complete. Output saved to {output_path}")
        return True
    
    def save_statistics(self, output_video_path):
        """Save counting statistics to JSON"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'video_file': str(self.video_path),
            'output_video': str(output_video_path),
            'total_entries': self.line_crossing.entry_count,
            'total_exits': self.line_crossing.exit_count,
            'net_count': self.line_crossing.entry_count - self.line_crossing.exit_count
        }
        
        stats_path = OUTPUTS_DIR / 'counts.json'
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Statistics saved to {stats_path}")
        return stats

if __name__ == "__main__":
    
    from config import VIDEO_FILE  
    
    counter = FootfallCounter()
    

    if VIDEO_FILE.exists():
        counter.process_video(VIDEO_FILE)
    else:
        logger.error(f"Video file not found: {VIDEO_FILE}")
        logger.info("Please ensure 'People entering and leaving modern building.mp4' is in the project root directory")
