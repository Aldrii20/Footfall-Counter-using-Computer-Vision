import numpy as np

class LineCrossing:
    def __init__(self, frame_height, line_position=0.5):
        """
        Initialize line crossing detector
        line_position: 0.0 to 1.0 (vertical position in frame)
        """
        self.line_y = int(frame_height * line_position)
        self.frame_height = frame_height
        self.entry_count = 0
        self.exit_count = 0
        self.crossed_objects = {}  
    def check_crossing(self, objectID, centroid_history):
        """
        Check if object crossed the line
        Returns: 'entry', 'exit', or None
        """
        if len(centroid_history) < 2:
            return None

        
        if objectID in self.crossed_objects:
            return None

        try:
            
            prev_centroid = np.array(list(centroid_history)[-2])
            curr_centroid = np.array(list(centroid_history)[-1])

            prev_y = int(prev_centroid[1])
            curr_y = int(curr_centroid[1])
        except:
            return None

        
        threshold = 5  

        
        if prev_y <= self.line_y and curr_y > self.line_y + threshold:
            self.crossed_objects[objectID] = 'entry'
            return 'entry'

        
        elif prev_y >= self.line_y and curr_y < self.line_y - threshold:
            self.crossed_objects[objectID] = 'exit'
            return 'exit'

        return None

    def update_counts(self, objectID, centroid_history):
        """Update entry/exit counts based on crossing"""
        
        if objectID in self.crossed_objects:
            return None

        direction = self.check_crossing(objectID, centroid_history)

        if direction == 'entry':
            self.entry_count += 1
        elif direction == 'exit':
            self.exit_count += 1

        return direction

    def get_line_coords(self, frame_width):
        """Get line coordinates for visualization"""
        return (0, self.line_y), (frame_width, self.line_y)
