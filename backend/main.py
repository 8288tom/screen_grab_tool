from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import subprocess
import os
from pathlib import Path
import shutil
import zipfile
import uuid
from cleanup import cleanup_screenshots_directory
import requests 

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"*": {"origins": "*"}})


def is_video_url(url):
    """Check if the URL points to a video by making a HEAD request and checking the Content-Type."""
    try:
        response = requests.head(url, allow_redirects=True)
        content_type = response.headers.get('Content-Type', '')
        return 'video/' or 'application/' in content_type  # Simple check for video MIME type
    except requests.RequestException as e:
        print(f"Error checking URL {url}: {e}")
        return False  # Assume not a video if any error occurs


@app.route('/screen_grab_tool/capture_and_download', methods=['POST'])
def capture_screenshots_and_zip():
    # Ensure the base directory for screenshots exists
    screenshots_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)

    if request.method == 'OPTIONS':
        # Handle preflight requests for CORS
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response
    
   
    # Parse data from the request
    data = request.get_json()
    times = data['times']
    video_link = data['videoLink']
    
    # Validations:
    if not video_link.startswith("http://") and not video_link.startswith("https://"):
        video_link = "https://" + video_link
    if not is_video_url(video_link):
        return jsonify({"error": "URL does not point to a valid video "}), 400
    # Create a unique directory for this session's screenshots
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(screenshots_dir, session_id)
    os.makedirs(session_dir, exist_ok=True)

    # Capture screenshots
    for index, time in enumerate(times, start=1):
        #Replace colons in the time string with another character (e.g., underscores or dashes)
        sanitized_time = time.replace(":", "-")
        filename = f"screenshot_{sanitized_time}.jpg"
        screenshot_path = os.path.join(session_dir, filename)
        cmd = [
            'ffmpeg', '-ss', time, '-i', video_link, '-vframes', '1', '-q:v', '2',
            screenshot_path
        ]
        try:
            result = subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            return jsonify({"error": str(e)}), 500


    # Create a ZIP file of the screenshots in the session directory
    zip_filename = f"{session_id}.zip"
    zip_file_path = os.path.join(screenshots_dir, zip_filename)  # Path for the ZIP file
    zip_path = shutil.make_archive(base_name=zip_file_path[:-4], format='zip', root_dir=session_dir)

    # Optionally, inspect the ZIP file contents
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_contents = zip_ref.namelist()
        print(f'Zip file was generated with: {zip_contents} for: {video_link}')
    
    if not zip_contents:
        return jsonify({"error": "ZIP file is empty."}), 500
    
    # Stream the ZIP file back to the client
    response = send_file(zip_path, as_attachment=True, download_name=zip_filename)
    cleanup_screenshots_directory()
    return response

if __name__ == '__main__':
    app.run(debug=True,port=5174)
