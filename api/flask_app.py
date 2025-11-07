import cv2
import json
import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import threading
from datetime import datetime
import logging

# Fix import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import OUTPUTS_DIR, VIDEOS_DIR
from main import FootfallCounter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='../templates')
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024  # 1GB max
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}

processing_jobs = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_video_background(job_id, input_path, output_path):
    """Process video in background thread"""
    try:
        logger.info(f"Starting background processing for job {job_id}")
        processing_jobs[job_id]['status'] = 'processing'
        processing_jobs[job_id]['progress'] = 0

        counter = FootfallCounter()
        counter.process_video(str(input_path), str(output_path))

        # Read statistics
        stats_path = OUTPUTS_DIR / 'counts.json'
        if stats_path.exists():
            with open(stats_path, 'r') as f:
                stats = json.load(f)
        else:
            stats = {'error': 'Stats file not found'}

        processing_jobs[job_id]['status'] = 'completed'
        processing_jobs[job_id]['progress'] = 100
        processing_jobs[job_id]['statistics'] = stats
        processing_jobs[job_id]['output_file'] = output_path.name

        logger.info(f"Job {job_id} completed successfully")

        if input_path.exists():
            os.remove(str(input_path))

    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        processing_jobs[job_id]['status'] = 'error'
        processing_jobs[job_id]['error'] = str(e)

@app.route('/', methods=['GET'])
def index():
    """Serve the web interface"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'FootfallCounter API'})

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Upload and process video"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400

        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(file.filename):
            allowed_str = ', '.join(ALLOWED_EXTENSIONS)
            return jsonify({'error': f'Invalid file type. Allowed: {allowed_str}'}), 400

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        job_id = f"{timestamp}_{filename}"

        input_path = VIDEOS_DIR / f"input_{job_id}"
        file.save(str(input_path))

        logger.info(f"File uploaded: {job_id}")

        output_path = OUTPUTS_DIR / f"output_{job_id}"

        processing_jobs[job_id] = {
            'status': 'queued',
            'progress': 0,
            'input_file': filename,
            'start_time': datetime.now().isoformat(),
            'statistics': None,
            'output_file': None,
            'error': None
        }

        thread = threading.Thread(
            target=process_video_background,
            args=(job_id, input_path, output_path),
            daemon=True
        )
        thread.start()

        logger.info(f"Started processing thread for job {job_id}")

        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Video uploaded. Processing started...'
        })

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get processing status"""
    if job_id not in processing_jobs:
        return jsonify({'error': 'Job not found'}), 404

    job = processing_jobs[job_id]
    return jsonify({
        'job_id': job_id,
        'status': job['status'],
        'progress': job['progress'],
        'statistics': job['statistics'],
        'error': job['error'],
        'start_time': job['start_time']
    })

@app.route('/api/download/<job_id>', methods=['GET'])
def download_video(job_id):
    """Download processed video"""
    if job_id not in processing_jobs:
        return jsonify({'error': 'Job not found'}), 404

    job = processing_jobs[job_id]
    if job['status'] != 'completed':
        return jsonify({'error': 'Video not ready yet'}), 400

    output_file = job['output_file']
    file_path = OUTPUTS_DIR / output_file

    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404

    try:
        return send_file(str(file_path), as_attachment=True, download_name=output_file)
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all processing jobs"""
    return jsonify({
        'total_jobs': len(processing_jobs),
        'jobs': {k: v for k, v in processing_jobs.items()}
    })

if __name__ == '__main__':
    VIDEOS_DIR.mkdir(exist_ok=True)
    OUTPUTS_DIR.mkdir(exist_ok=True)
    logger.info("Starting Footfall Counter Flask App on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)