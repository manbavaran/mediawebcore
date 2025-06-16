# mediawebcore

**Web-based real-time webcam streaming server**  
Designed for use with AI-powered visual applications like virtual pianos.

---

## 🚀 Features

- Real-time webcam to server video transmission (base64)
- Input/output video size control (pixels or percentages)
- Audio send/receive flags (server-side controlled)
- Responsive layout: top-bottom, left-right, center
- Plugin support via `on_frame(frame)` callback

---

## 🔧 Installation

```bash
pip install .



🖥️ Usage (CLI)

mediawebcore --input-size 640x480 --output-size 100%x50% --layout top-bottom


📁 Example Python integration
from mediawebcore.core import run_server

def custom_processing(frame):
    # your OpenCV logic here
    return frame

run_server(
    video_size_input=["100%", "50%"],
    video_size_output=["100%", "50%"],
    on_frame=custom_processing
)



🧩 Plugin Architecture
Use on_frame callback to inject your own frame analysis logic
(e.g. pose detection, hand tracking, segmentation).


📜 License
MIT License