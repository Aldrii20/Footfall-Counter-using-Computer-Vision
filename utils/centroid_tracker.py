import numpy as np
from scipy.spatial import distance
from collections import defaultdict, deque

class CentroidTracker:
    def __init__(self, maxDisappeared=40, maxDistance=50):
        """
        Initialize centroid tracker
        maxDisappeared: frames to wait before removing object
        maxDistance: max pixel distance for centroid matching
        """
        self.nextObjectID = 0
        self.objects = {}
        self.disappeared = defaultdict(int)
        self.maxDisappeared = maxDisappeared
        self.maxDistance = maxDistance
        self.centroids_history = defaultdict(deque)
    
    def register(self, centroid):
        """Register new object"""
        self.objects[self.nextObjectID] = centroid
        self.centroids_history[self.nextObjectID] = deque(maxlen=10)
        self.centroids_history[self.nextObjectID].append(centroid)
        self.nextObjectID += 1
    
    def deregister(self, objectID):
        """Remove inactive object"""
        del self.objects[objectID]
        del self.disappeared[objectID]
        del self.centroids_history[objectID]
    
    def update(self, rects):
        """
        Update centroids with current frame detections
        rects: array of [x1, y1, x2, y2, ...]
        Returns: dict {objectID: centroid}
        """
        if len(rects) == 0:
            
            disappearedIDs = list(self.disappeared.keys())
            for objectID in disappearedIDs:
                self.disappeared[objectID] += 1
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)
            return self.objects
        
        
        inputCentroids = np.zeros((len(rects), 2), dtype="int")
        for i, (x1, y1, x2, y2) in enumerate(rects[:, :4]):
            cX = (x1 + x2) // 2
            cY = (y1 + y2) // 2
            inputCentroids[i] = [cX, cY]
        
        if len(self.objects) == 0:
           
            for i in range(len(inputCentroids)):
                self.register(inputCentroids[i])
        else:
        
            objectIDs = list(self.objects.keys())
            objectCentroids = [self.objects[objID] for objID in objectIDs]
            
            D = distance.cdist(np.array(objectCentroids), inputCentroids)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            usedRows = set()
            usedCols = set()
            
            for (row, col) in zip(rows, cols):
                if D[row, col] > self.maxDistance:
                    continue
                
                objectID = objectIDs[row]
                self.objects[objectID] = inputCentroids[col]
                self.centroids_history[objectID].append(inputCentroids[col])
                self.disappeared[objectID] = 0
                
                usedRows.add(row)
                usedCols.add(col)
            
            
            unusedRows = set(range(D.shape[0])).difference(usedRows)
            unusedCols = set(range(D.shape[1])).difference(usedCols)

            for row in unusedRows:
                objectID = objectIDs[row]
                self.disappeared[objectID] += 1
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)

            for col in unusedCols:
                self.register(inputCentroids[col])

        return self.objects
