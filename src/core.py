from flask import Flask, render_template
from flask_socketio import SocketIO
import base64
import cv2
import numpy as np
import eventlet
import os

eventlet.monkey_patch()

def _clean_percent_str(val):
    """
    % 문자열일 경우: 앞뒤/중간 공백 제거, 'N%' 또는 'NN%' 등
    1~100% 만 허용, 아니면 None 반환
    """
    if isinstance(val, str):
        val = val.strip().replace(' ', '')
        if val.endswith('%') and val[:-1].isdigit():
            num = int(val[:-1])
            if 1 <= num <= 100:
                return f"{num}%"
    return None

def run_server(
    host="0.0.0.0",
    port=5000,
    template="index.html",
    on_frame=None,
    video_size=[320, 240]  # [가로, 세로] (정수 픽셀 or 'NN%' 문자, 1~100%만 허용)
):
    # 1. video_size 유효성 검사/정리
    assert isinstance(video_size, (list, tuple)) and len(video_size) == 2, \
        "video_size는 [가로, 세로] 리스트/튜플이어야 함!"
    width, height = video_size
    for v in [width, height]:
        if isinstance(v, int):
            continue
        elif isinstance(v, str):
            cleaned = _clean_percent_str(v)
            if not cleaned:
                raise ValueError("video_size 각 값은 정수(픽셀) 또는 1~100%의 'NN%' 형식만 허용합니다!")
        else:
            raise ValueError("video_size 각 값은 정수(픽셀) 또는 1~100%의 'NN%' 형식만 허용합니다!")
    width = _clean_percent_str(width) if isinstance(width, str) else width
    height = _clean_percent_str(height) if isinstance(height, str) else height

    # 2. Flask/SocketIO 인스턴스 생성
    app = Flask(__name__, template_folder="templates")
    socketio = SocketIO(app, cors_allowed_origins='*')

    @app.route("/")
    def index():
        return render_template(
            template,
            width=width,
            height=height
        )

    @socketio.on('frame')
    def handle_frame(data):
        # base64 → OpenCV 이미지
        header, encoded = data.split(',', 1)
        img_bytes = base64.b64decode(encoded)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # 서비스 콜백 있으면 분석/가공 (예: 손 추적, 좌우반전 등)
        if on_frame:
            result_frame = on_frame(frame)
        else:
            result_frame = frame

        # 결과 프레임 → base64 변환/전송
        _, buffer = cv2.imencode('.jpg', result_frame)
        out_base64 = base64.b64encode(buffer).decode('utf-8')
        out_data_url = f"data:image/jpeg;base64,{out_base64}"
        socketio.emit('result_frame', out_data_url)

    print(f"\n[mediawebcore] 서버 구동: http://{host}:{port}/ (Ctrl+C 종료)\n")
    socketio.run(app, host=host, port=port, debug=True)
