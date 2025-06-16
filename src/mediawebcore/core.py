# 파일: mediawebcore/core.py
from flask import Flask, render_template
from flask_socketio import SocketIO,emit
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

    
    @socketio.on("frame_blob")
    def handle_frame_blob(data):
        try:
            # ▶️ 바이너리 blob → NumPy 배열 (이미지 디코딩)
            np_arr = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                print("⚠️ 이미지 디코딩 실패")
                return

            # ✅ 처리: 여기서 frame을 원하는 방식으로 분석/변형 가능
            result_frame = frame  # 예시: 그대로 되돌려줌

            # ⏺️ 결과 프레임 → JPEG 인코딩
            success, buffer = cv2.imencode(".jpg", result_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not success:
                print("⚠️ JPEG 인코딩 실패")
                return

            # 🔁 클라이언트로 이진 blob 전송
            emit("result_frame_blob", buffer.tobytes(), binary=True)

        except Exception as e:
            print(f"❌ 처리 중 오류 발생: {e}")

    socketio.run(app, host=host, port=port, debug=True)
