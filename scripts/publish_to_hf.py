#!/usr/bin/env python3
"""
Publish a locally trained YOLO model to the Hugging Face Hub.

Use this when you trained outside the Colab notebook and just want to push
weights. The notebook already does this inline; this is the standalone version.

Example:
    pip install huggingface_hub
    huggingface-cli login        # or pass --token
    python scripts/publish_to_hf.py \\
        --repo youruser/traffic-signs-v1 \\
        --pt runs/train/weights/best.pt \\
        --onnx runs/train/weights/best.onnx
"""
import argparse
import os
from huggingface_hub import HfApi, ModelCard, login


def main():
    p = argparse.ArgumentParser(description="Upload YOLO weights to Hugging Face.")
    p.add_argument("--repo", required=True, help="e.g. youruser/model-id")
    p.add_argument("--pt", required=True, help="path to best.pt")
    p.add_argument("--onnx", help="path to best.onnx (optional but recommended)")
    p.add_argument("--token", help="HF write token (or run huggingface-cli login first)")
    p.add_argument("--private", action="store_true", help="create a private repo")
    args = p.parse_args()

    if args.token:
        login(token=args.token)

    api = HfApi()
    api.create_repo(args.repo, repo_type="model", exist_ok=True, private=args.private)

    api.upload_file(path_or_fileobj=args.pt, path_in_repo="best.pt", repo_id=args.repo)
    print(f"uploaded best.pt ({round(os.path.getsize(args.pt) / 1e6, 1)} MB)")

    if args.onnx:
        api.upload_file(path_or_fileobj=args.onnx, path_in_repo="best.onnx", repo_id=args.repo)
        print("uploaded best.onnx")

    # Minimal card so the HF page isn't blank
    model_id = args.repo.split("/")[-1]
    ModelCard(
        "---\ntags: [object-detection, yolo, ultralytics]\nlicense: agpl-3.0\n---\n\n"
        f"# {model_id}\n\nYOLO model trained for object detection. Part of the ModelBox catalog.\n"
    ).push_to_hub(args.repo)

    print(f"done -> https://huggingface.co/{args.repo}")
    print(f"download URL: https://huggingface.co/{args.repo}/resolve/main/best.pt")


if __name__ == "__main__":
    main()