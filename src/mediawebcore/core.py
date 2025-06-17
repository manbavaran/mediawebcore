# 파일: mediawebcore/core.py
from flask import Flask, render_template
from flask_socketio import SocketIO
import cv2
import numpy as np
import eventlet
import logging

# 필수 패치 먼저
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
    layout="top-bottom",
    render_mode="default"
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
            render_mode=render_mode
        )

    @socketio.on("frame_blob")
    def handle_frame_blob(data):
        def process_frame(data):
            try:
                np_arr = np.frombuffer(data, dtype=np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if frame is None:
                    print("\u26a0\ufe0f 이미지 디코딩 실패")
                    return

                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (480, 360))

                if on_frame:
                    result_frame, crop_rect = on_frame(frame)
                    render_info = {
                        "render_mode": render_mode,
                        "width": result_frame.shape[1],
                        "height": result_frame.shape[0]
                    }
                    if crop_rect:
                        x, y, w, h = crop_rect
                        result_frame = result_frame[y:y+h, x:x+w]
                        render_info["cropped"] = True
                    else:
                        render_info["cropped"] = False
                else:
                    result_frame = frame
                    render_info = {
                        "render_mode": render_mode,
                        "width": result_frame.shape[1],
                        "height": result_frame.shape[0],
                        "cropped": False
                    }

                if result_frame is None or result_frame.size == 0:
                    print("\u26a0\ufe0f result_frame is empty")
                    return

                success, buffer = cv2.imencode(".webp", result_frame, [cv2.IMWRITE_WEBP_QUALITY, 70])
                if not success:
                    print("\u26a0\ufe0f WebP 인코딩 실패")
                    return

                socketio.emit("result_frame_blob", {
                    "image": buffer.tobytes(),
                    **render_info
                })

            except Exception as e:
                print(f"\u274c 처리 중 오류 발생: {e}")

        socketio.start_background_task(process_frame, data)

    socketio.run(app, host=host, port=port, debug=True)
