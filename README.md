# OptiForge

A lightweight, locally-hosted web app for compressing and resizing game asset images. Built with Flask and Pillow — no cloud required, no data leaves your machine.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-black?logo=flask)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

| Feature | What it does |
|---|---|
| **Multi-file upload** | Drag & drop or browse — process many images at once |
| **Format conversion** | Output as PNG (lossless), JPG (quality control), or WEBP |
| **Quality control** | Adjustable quality slider (10–100) for JPG and WEBP output |
| **Resize** | Optional width × height resize with aspect-ratio lock |
| **Batch ZIP export** | All optimized files bundled into a single `optimized.zip` |
| **Savings report** | Per-file and total size savings shown in the results table |

---

## Requirements

### Software

| Requirement | Version | Notes |
|---|---|---|
| [Python](https://www.python.org/downloads/) | 3.11+ | Required |

### Python packages

All listed in `requirements.txt`:

```
flask>=3.0.0
pillow>=10.0.0
flask-limiter>=3.5.0
gunicorn>=21.0.0
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/CMGForge/optiforge.git
cd optiforge
```

### 2. Create and activate a virtual environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Running locally

```bash
python optiforge.py
```

The server starts on `http://127.0.0.1:5000` and opens in your browser automatically.

---

## Project structure

```
optiforge/
├── optiforge.py         # Flask app — all routes and business logic
├── requirements.txt     # Python dependencies
├── Procfile             # Gunicorn entry point (for deployment)
├── templates/
│   └── index.html       # Single-page UI (HTML + CSS + JS)
└── static/              # Static assets (if any)
```

---

## API Routes

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Main UI page |
| `POST` | `/api/optimize` | Compress / resize images, returns `optimized.zip` |

### POST `/api/optimize` — fields

| Field | Type | Description |
|---|---|---|
| `images[]` | file(s) | One or more image files |
| `format` | string | Output format: `png`, `jpg`, or `webp` |
| `quality` | int | Compression quality 10–100 (JPG / WEBP only) |
| `resize` | string | `"true"` to enable resizing |
| `width` | int | Target width in pixels (optional) |
| `height` | int | Target height in pixels (optional) |
| `lock_aspect` | string | `"true"` to preserve aspect ratio |

Returns a ZIP file (`Content-Type: application/zip`) with an `X-Results` header containing base64-encoded JSON with per-file size data.

---

## Deployment

The app is production-ready with Gunicorn. It can be deployed to any WSGI-compatible host.

**Render / Railway / Fly.io:**

The `Procfile` is already configured:

```
web: gunicorn optiforge:app --workers 2 --timeout 120 --bind 0.0.0.0:$PORT
```

Just connect your GitHub repo and deploy — no extra configuration needed.

---

## License

MIT — see [LICENSE](LICENSE) for details.

© CMG Forge
