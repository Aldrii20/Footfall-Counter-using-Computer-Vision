Footfall-Counter-using-Computer-Vision
Detects and counts people entering and exiting a defined area in video—using YOLOv8 detection, centroid tracking, and a robust line-crossing logic. Provides a Flask web interface for uploading and processing videos.

Approach
Person Detection:

Uses YOLOv8 (Ultralytics) to detect humans in every frame.

Tracking:

Associates detections using centroid tracking (each person gets a unique ID).

Counting Logic:

Defines a virtual line .

Whenever a tracked person crosses the line, increments the entry or exit count.

Ensures each person is counted only once, using a per-ID latch and a small pixel threshold to avoid jittered double-counting.

Visualization:

Draws bounding boxes, IDs, line, and counts directly on the video output.

Web UI shows live progress, entries, exits.

Video Source
Example: YouTube – People entering and leaving modern building

You can use any clear entry/exit video; tested with the above public footage.

Counting Logic Explanation
Each detection is assigned a unique ID as it enters the scene.

The virtual line (set in config.py via LINE_POSITION) divides the entry and exit space.

For every tracked individual, the algorithm checks previous and current Y-coordinate positions:

If crossing direction is top to bottom: entry is counted.

If crossing bottom to top: exit is counted.

For each ID, only the first valid crossing is registered, preventing repeated counts.

A pixel threshold filters out small movements and noise near the counting line.

Dependencies
Python 3.12+

opencv-python >= 4.9.0

ultralytics >= 8.0.205

torch >= 2.1.0

torchvision >= 0.16.0

flask >= 3.0.0

Video link :https://youtu.be/-rtIP5Jrk58?si=eAVgkr9oDxI4TrR6
