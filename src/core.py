from flask import Flask, render_template
from flask_socketio import SocketIO
import base64
import cv2
import numpy as np
import eventlet

eventlet.monkey_patch()

def _clean_percent_str(val):
    """퍼센트 문자열(1~100%)만 허용, 아니면 None"""
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
    video_size_input=None,    # 예: [320, 240] 또는 ["80%", "60%"] (없으면 미리보기 X)
    video_size_output=None,   # 예: [320, 240] 또는 ["100%", "80%"] (없으면 결과 영상 X)
    audio_send=False,
    audio_receive=True,
):
    # video_size_input/ video_size_output: [가로, 세로] (정수 또는 'NN%')
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
                raise ValueError("비디오 사이즈는 정수 또는 1~100% 'NN%'만 허용")
        w = _clean_percent_str(w) if isinstance(w, str) else w
        h = _clean_percent_str(h) if isinstance(h, str) else h
        return w, h

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
        )

    @socketio.on('frame')
    def handle_frame(data):
        header, encoded = data.split(',', 1)
        img_bytes = base64.b64decode(encoded)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if on_frame:
            result_frame = on_frame(frame)
        else:
            result_frame = frame

        _, buffer = cv2.imencode('.jpg', result_frame)
        out_base64 = base64.b64encode(buffer).decode('utf-8')
        out_data_url = f"data:image/jpeg;base64,{out_base64}"
        socketio.emit('result_frame', out_data_url)

    print(f"\n[mediawebcore] 서버 구동: http://{host}:{port}/ (Ctrl+C 종료)\n")
    socketio.run(app, host=host, port=port, debug=True)
