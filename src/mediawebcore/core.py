# 파일: mediawebcore/core.py
from flask import Flask, render_template
from flask_socketio import SocketIO
import cv2
import numpy as np
import eventlet
import logging

eventlet.monkey_patch()
logger = logging.getLogger("mediawebcore")
logger.setLevel(logging.DEBUG)

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
        logger.info("📄 index.html 렌더링 요청됨")
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
        def process_frame(data):
            try:
                logger.debug("📥 frame_blob 수신")
                np_arr = np.frombuffer(data, dtype=np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if frame is None:
                    logger.warning("⚠️ 이미지 디코딩 실패")
                    return

                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (480, 360))
                crop_rect = None

                if on_frame:
                    try:
                        _, crop_rect = on_frame(frame)
                    except Exception as e:
                        logger.exception(f"❌ on_frame 처리 오류: {e}")

                success, buffer = cv2.imencode(".webp", frame, [cv2.IMWRITE_WEBP_QUALITY, 70])
                if not success:
                    logger.error("❌ WebP 인코딩 실패")
                    return

                socketio.emit("result_frame_blob", {
                    "image": buffer.tobytes(),
                    "cropped": crop_rect is not None,
                    "render_mode": "bottom" if crop_rect else "default",
                    "crop_rect": crop_rect
                })
                logger.debug("📤 result_frame_blob 전송 완료")

            except Exception as e:
                logger.exception(f"❌ 처리 중 오류: {e}")

        socketio.start_background_task(process_frame, data)

    logger.info(f"🚀 서버 실행 중: http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=True)
