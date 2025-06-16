# 파일: mediawebcore/core.py
from flask import Flask, render_template
from flask_socketio import SocketIO
import base64
import cv2
import numpy as np
import eventlet
import logging

eventlet.monkey_patch()
logger = logging.getLogger("mediawebcore")
logger.setLevel(logging.INFO)

def _clean_percent_str(val):
    if isinstance(val, str):
        val = val.strip().replace(' ', '')
        if val.endswith('%') and val[:-1].isdigit():
            num = int(val[:-1])
            if 1 <= num <= 100:
                return f"{num}%"
    return None

def _check_size(sz):
    if sz is None:
        return (None, None)
    assert isinstance(sz, (list, tuple)) and len(sz) == 2
    w, h = sz
    for v in (w, h):
        if isinstance(v, int):
            continue
        elif isinstance(v, str) and _clean_percent_str(v):
            continue
        else:
            raise ValueError("video size must be int or 'NN%'")
    w = _clean_percent_str(w) if isinstance(w, str) else w
    h = _clean_percent_str(h) if isinstance(h, str) else h
    return w, h

def run_server(
    host="0.0.0.0",
    port=5000,
    template="index.html",
    on_frame=None,
    video_size_input=None,
    video_size_output=None,
    audio_send=False,
    audio_receive=True,
    layout="top-bottom"
):
    input_width, input_height = _check_size(video_size_input)
    output_width, output_height = _check_size(video_size_output)

    app = Flask(__name__, template_folder="templates")
    socketio = SocketIO(app, cors_allowed_origins='*')

    @app.route("/")
    def index():
        return render_template(
            template,
            input_width=input_width,
            input_height=input_height,
            output_width=output_width,
            output_height=output_height,
            audio_send=audio_send,
            audio_receive=audio_receive,
            layout=layout,
        )

    @socketio.on('frame')
    def handle_frame(data):
        try:
            header, encoded = data.split(',', 1)
            img_bytes = base64.b64decode(encoded)
            img_array = np.frombuffer(img_bytes, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if frame is None:
                raise ValueError("cv2.imdecode failed")

            result_frame = on_frame(frame) if on_frame else frame

            _, buffer = cv2.imencode('.jpg', result_frame)
            out_base64 = base64.b64encode(buffer).decode('utf-8')
            out_data_url = f"data:image/jpeg;base64,{out_base64}"
            socketio.emit('result_frame', out_data_url)
        except Exception as e:
            logger.warning(f"Frame handling error: {e}")

    socketio.run(app, host=host, port=port, debug=True)
