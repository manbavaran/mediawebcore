from flask import Flask, render_template
from flask_socketio import SocketIO
import eventlet
import base64
from datetime import datetime
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

eventlet.monkey_patch()
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on('frame')
def handle_frame(data):
    # base64 to OpenCV image
    header, encoded = data.split(',', 1)
    img_bytes = base64.b64decode(encoded)
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    # 1. 좌우반전 (미러)
    flipped_frame = cv2.flip(frame, 1)
    
    # 2. 다시 JPEG로 변환
    _, buffer = cv2.imencode('.jpg', flipped_frame)
    flipped_base64 = base64.b64encode(buffer).decode('utf-8')
    flipped_data_url = f"data:image/jpeg;base64,{flipped_base64}"
    
    
    # 3. 클라로 송신 (result_frame 이벤트)
    socketio.emit('result_frame', flipped_data_url)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
