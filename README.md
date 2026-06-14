# ComputerVisionAIHub

An open catalog of custom-trained **YOLO** models. Browse models on a static
GitHub Pages site, download the weights from the Hugging Face Hub, and run them
locally with one Docker command.

> **Rename it:** "ComputerVisionAIHub" appears in `docs/index.html` (title + brand),
> `docs/styles.css` (only as a comment), `docs/app.js` (`DOCKER_IMAGE`),
> and this file. Search-and-replace to rebrand.

## How it works

```
Roboflow dataset ──► Google Colab (train YOLO26) ──► Hugging Face Hub (weights)
                                                            │
   GitHub repo (code) ──► GitHub Pages (catalog) ───────────┘ links to downloads
                                   │
                          user downloads + runs via Docker
```

The website holds **no model files** — only `docs/models.json`, which lists each
model and points to its weights on Hugging Face. Weights live on the Hub (free,
unlimited public storage). This keeps the repo tiny and the site fast.

## Repo layout

```
docs/         GitHub Pages site (set Pages source to /docs)
  index.html  structure
  styles.css  design tokens + the bounding-box card styling
  app.js      fetches models.json and renders the catalog
  models.json THE CATALOG — add a model by appending one entry here
notebooks/
  train_yolo26.ipynb   end-to-end training + publishing (open in Colab)
scripts/
  publish_to_hf.py     push existing weights to Hugging Face from your terminal
inference/
  Dockerfile  detect.py  app.py  requirements.txt   local model runner
LICENSE       AGPL-3.0
```

## For users: run a model

Every catalog card has a copy-paste command. The model argument is the Hugging
Face URL — the container downloads it on first run.

```bash
# build once
docker build -t computervisionaihub ./inference

# CLI: annotate one image
docker run -v $(pwd):/data computervisionaihub \
  https://huggingface.co/youruser/traffic-signs-v1/resolve/main/best.pt \
  /data/test.jpg

# web UI: drag-and-drop at http://localhost:7860
docker run -p 7860:7860 --entrypoint python computervisionaihub app.py
```

## For maintainers: add a model

1. Open `notebooks/train_yolo26.ipynb` in Google Colab, set runtime to a **T4 GPU**.
2. Fill in your Roboflow + Hugging Face details and run all cells. It trains
   YOLO26, exports `.pt` + `.onnx`, pushes them to the Hub, and **prints a
   ready-to-paste `models.json` entry**.
3. Paste that entry into the `models` array in `docs/models.json`, edit the
   human-readable fields (name, summary, dataset link, license), and commit.

That's it — no website code changes. (Trained locally instead? Use
`python scripts/publish_to_hf.py --repo youruser/model-id --pt best.pt --onnx best.onnx`.)

## Set up GitHub Pages

Repo **Settings → Pages → Build and deployment → Source: Deploy from a branch →
Branch: `main`, folder: `/docs`**. Your catalog goes live at
`https://youruser.github.io/yolo-model-hub/`.

## Local preview

The site fetches `models.json`, so open it through a server (not `file://`):

```bash
cd docs && python -m http.server
# visit http://localhost:8000
```

## A note on licensing

Ultralytics YOLO is **AGPL-3.0**, a strong copyleft license. Because the training
notebook and Docker image use the Ultralytics library, this repo is AGPL-3.0 too.
Two practical consequences:

- Anyone redistributing or network-serving Ultralytics-based code inherits AGPL
  obligations. That's fine for an open project, but worth telling your users.
- The **ONNX** export can be run with `onnxruntime` *without* Ultralytics, letting
  downstream users avoid AGPL in their own apps. That's why every model ships both
  formats.

Each model's underlying **dataset** has its own license (shown on each card).
Check it before any commercial use.