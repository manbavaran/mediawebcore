from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import cv2
import numpy as np
import logging

logger = logging.getLogger("mediawebcore")
logger.setLevel(logging.INFO)

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
    app = Flask(__name__, template_folder="templates")
    socketio = SocketIO(app, cors_allowed_origins='*', compression=False)

    @app.route("/")
    def index():
        return render_template(
            template,
            input_width=None,  # 미리보기 제거
            input_height=None,
            output_width="100%",
            output_height="100%",
            audio_send=audio_send,
            audio_receive=audio_receive,
            layout=layout,
        )

    @socketio.on("frame_blob")
    def handle_frame_blob(data):
        def process_frame(data):
            try:
                # 바이너리 blob → NumPy 배열
                np_arr = np.frombuffer(data, dtype=np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if frame is None:
                    print("⚠️ 이미지 디코딩 실패")
                    return

                # 좌우 반전
                frame = cv2.flip(frame, 1)

                # 해상도 축소 (320x240)
                frame = cv2.resize(frame, (320, 240))

                # 처리 로직 (원본 그대로 사용)
                result_frame = frame

                # WebP 인코딩
                success, buffer = cv2.imencode(".webp", result_frame, [cv2.IMWRITE_WEBP_QUALITY, 50])
                if not success:
                    print("⚠️ WebP 인코딩 실패")
                    return

                # binary=True 제거 (자동 처리됨)
                socketio.emit("result_frame_blob", buffer.tobytes())

            except Exception as e:
                print(f"❌ 처리 중 오류 발생: {e}")

        socketio.start_background_task(process_frame, data)

    socketio.run(app, host=host, port=port, debug=True)
