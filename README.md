# mediawebcore

**Web-based real-time webcam streaming server**  
Modular and plugin-ready, ideal for AI-powered visual applications such as virtual pianos.

---

🚀 Features
🔁 Real-time webcam streaming via WebSocket + binary Blob (high performance)

🖼️ Image transmission using WebP format (smaller size, better speed)

⬇️ Server-side resolution downscaling for reduced bandwidth

⬆️ Client-side resolution upscaling to fullscreen (canvas-based)

💡 Flip (mirror) view applied for natural UX alignment

🖥️ Only server stream is displayed on client (no local webcam preview)

🔧 Socket.IO compression disabled for reduced latency

🧵 Multithreaded processing on server for responsiveness

🎛️ Modular on_frame(frame) plugin architecture for custom AI/vision pipelines

📐 Input/output video size control (pixels or %)

🔊 Server-side audio toggle (send/receive)

📐 Flexible layout options: top-bottom, left-right, center, corners

🌐 External access support via Nginx or ngrok (optional)



## 🔧 Installation

git clone https://github.com/yourname/mediawebcore.git
cd mediawebcore
pip install .


🖥️ Usage (CLI)
mediawebcore run \
  --input-size 640x480 \
  --output-size 100%x50% \
  --layout top-bottom \
  --audio-send false \
  --audio-receive true \
  --nginx false \
  --ngrok false


📁 Python Integration Example
from mediawebcore.core import run_server

def custom_processing(frame):
    # Example: image analysis with OpenCV
    return frame

run_server(
    video_size_input=["100%", "50%"],
    video_size_output=["100%", "50%"],
    on_frame=custom_processing
)


🧩 Plugin Architecture
Customize the processing pipeline by injecting your own logic into the on_frame(frame) callback.

Examples:

Hand tracking (MediaPipe)

Object detection (YOLO, SSD)

Pose estimation

AI segmentation


🌐 External Access (Optional)
Nginx: Recommended for production environments (reverse proxy, domain, SSL)

ngrok: Instant testing with public URLs (requires ngrok)

These tools are not bundled, and users must install/configure them separately.


📜 License
This project is licensed under the MIT License. See the LICENSE file for details.