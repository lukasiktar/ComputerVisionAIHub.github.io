# Contributing a model to ComputerVisionAIHub

Thanks for adding a model! The catalog is driven entirely by `docs/models.json`.
Contributing means training a model, hosting its weights on the Hugging Face Hub,
and opening a pull request that adds one entry to that file. A GitHub Action checks
your entry automatically.

## Workflow

1. **Train.** Open `notebooks/train_yolo26.ipynb` in Google Colab or locally. Point
   it at a Roboflow dataset and run all cells.
2. **Publish weights.** The notebook pushes `best.pt` and `best.onnx` to a
   Hugging Face model repo under your account and prints a `models.json` entry.
   (Trained locally? Use `python scripts/publish_to_hf.py --help`.)
3. **Add the entry.** Paste the printed object into the `models` array in
   `docs/models.json`. Fill in the human-readable fields.
4. **Validate locally** (optional but recommended):
   ```bash
   python scripts/validate_models.py --check-links
   ```
5. **Open a pull request.** The Action re-runs validation. Once it's green, a
   maintainer merges and your model appears on the site.

## Entry schema

```jsonc
{
  "id": "traffic-signs-v1",          // required · lowercase slug, must be unique
  "name": "Traffic Sign Detector",   // required · shown as the card title
  "summary": "Detects road signs.",  // one line under the title
  "base_model": "yolo26n",           // required · yolo26n/s/m/l, yolo11n, etc.
  "task": "detection",               // detection | segmentation | classification | pose | obb
  "classes": ["stop", "yield"],      // required · non-empty list of class names
  "dataset": "https://universe.roboflow.com/...",  // source dataset (https)
  "dataset_license": "CC BY 4.0",    // the dataset's license — please set this
  "metrics": { "mAP50": 0.91, "mAP50_95": 0.74 },  // numbers between 0 and 1
  "hf_repo": "youruser/traffic-signs-v1",
  "download": "https://huggingface.co/youruser/traffic-signs-v1/resolve/main/best.pt", // required
  "onnx": "https://huggingface.co/youruser/traffic-signs-v1/resolve/main/best.onnx",
  "size_mb": 6.2,
  "image_size": 640,
  "updated": "2026-06-01"
}
```

## What the validator checks

- `models.json` is valid JSON.
- Required fields are present and non-empty: `id`, `name`, `base_model`, `task`, `download`.
- `id` is a lowercase slug and unique across the catalog.
- `classes` is a non-empty list.
- `metrics.mAP50` / `metrics.mAP50_95` are numbers between 0 and 1 (if present).
- `download`, `onnx`, `dataset` are `https://` URLs.
- With `--check-links`: `download` and `onnx` URLs resolve (a 404 fails the build).

Missing a `dataset_license` is a warning, not a failure — but please include it.

## Ground rules

- **Weights go on Hugging Face, never in this repo.** `.pt` and `.onnx` files are
  git-ignored on purpose.
- **Respect dataset licenses.** Only submit models trained on datasets you're
  allowed to use, and record the license accurately.
- **Ship both formats** when you can. The `.onnx` export lets people run your
  model without the AGPL-licensed Ultralytics library.