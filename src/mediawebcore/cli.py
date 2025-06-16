# 파일: mediawebcore/cli.py
import argparse
from .core import run_server

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-size", type=str, default="320x240")
    parser.add_argument("--output-size", type=str, default="100%x80%")
    parser.add_argument("--audio-send", action="store_true")
    parser.add_argument("--no-audio-receive", action="store_true")
    parser.add_argument("--layout", type=str, default="top-bottom")
    args = parser.parse_args()

    def parse_size(s):
        if 'x' in s:
            w, h = s.split('x')
            return [w.strip(), h.strip()]
        return None

    run_server(
        video_size_input=parse_size(args.input_size),
        video_size_output=parse_size(args.output_size),
        audio_send=args.audio_send,
        audio_receive=not args.no_audio_receive,
        layout=args.layout
    )
