#!/usr/bin/env python3
"""
Run a YOLO model on an image.

The model argument can be EITHER a local file path OR a URL (e.g. a Hugging Face
download link copied from the ModelBox catalog).

Usage (inside the Docker container):
    python detect.py <model.pt | URL> <image_path> [output_path]

Example:
    python detect.py \\
        https://huggingface.co/youruser/traffic-signs-v1/resolve/main/best.pt \\
        /data/test.jpg /data/output.jpg
"""
import sys
import os
import urllib.request
from ultralytics import YOLO


def resolve_model(arg: str) -> str:
    """If arg is a URL, download to /tmp and return the local path; else return as-is."""
    if arg.startswith("http://") or arg.startswith("https://"):
        local = os.path.join("/tmp", os.path.basename(arg.split("?")[0]) or "model.pt")
        if not os.path.exists(local):
            print(f"downloading model -> {local}")
            urllib.request.urlretrieve(arg, local)
        return local
    return arg


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    model_arg = sys.argv[1]
    image_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else "/data/output.jpg"

    model = YOLO(resolve_model(model_arg))
    results = model(image_path)

    # Save the annotated image
    results[0].save(output_path)
    print(f"saved annotated image -> {output_path}")

    # Print detections as text
    boxes = results[0].boxes
    names = model.names
    print(f"\n{len(boxes)} detection(s):")
    for b in boxes:
        cls = names[int(b.cls)]
        conf = float(b.conf)
        print(f"  {cls:<20} {conf:.2f}")


if __name__ == "__main__":
    main()