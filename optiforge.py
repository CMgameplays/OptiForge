import io
import os
import sys
import zipfile
import webbrowser
import threading
from flask import Flask, render_template, request, send_file, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from PIL import Image

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "60 per hour"],
    storage_uri="memory://",
)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def optimize_image(
    img: Image.Image,
    fmt: str,
    quality: int,
    resize: bool,
    width: int | None,
    height: int | None,
    lock_aspect: bool,
) -> bytes:
    """Process a single image and return optimized bytes."""
    if resize and (width or height):
        orig_w, orig_h = img.size
        if lock_aspect:
            if width and height:
                ratio = min(width / orig_w, height / orig_h)
                width = int(orig_w * ratio)
                height = int(orig_h * ratio)
            elif width:
                height = int(orig_h * (width / orig_w))
            else:
                width = int(orig_w * (height / orig_h))
        target_w = width or orig_w
        target_h = height or orig_h
        img = img.resize((target_w, target_h), Image.LANCZOS)

    buf = io.BytesIO()

    if fmt == "png":
        # Convert to RGBA for PNG to preserve transparency
        if img.mode not in ("RGB", "RGBA", "L", "LA", "P"):
            img = img.convert("RGBA")
        img.save(buf, format="PNG", optimize=True, compress_level=9)

    elif fmt == "jpg":
        # JPEG does not support transparency
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")
        img.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)

    elif fmt == "webp":
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        img.save(buf, format="WEBP", quality=quality, method=6)

    return buf.getvalue()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/optimize", methods=["POST"])
@limiter.limit("30 per minute")
def api_optimize():
    files = request.files.getlist("images[]")
    if not files or all(f.filename == "" for f in files):
        return jsonify({"error": "No images provided"}), 400

    fmt = request.form.get("format", "png").lower()
    if fmt not in ("png", "jpg", "webp"):
        return jsonify({"error": "Invalid format"}), 400

    try:
        quality = int(request.form.get("quality", 85))
        quality = max(10, min(100, quality))
    except (TypeError, ValueError):
        quality = 85

    resize = request.form.get("resize", "false").lower() == "true"
    lock_aspect = request.form.get("lock_aspect", "true").lower() == "true"

    try:
        width = int(request.form.get("width", 0)) or None
        height = int(request.form.get("height", 0)) or None
    except (TypeError, ValueError):
        width = height = None

    zip_buf = io.BytesIO()
    results = []

    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            if not f or f.filename == "":
                continue
            if not allowed_file(f.filename):
                continue

            original_bytes = f.read()
            original_size = len(original_bytes)

            try:
                img = Image.open(io.BytesIO(original_bytes))
                img.load()
            except Exception:
                continue

            optimized = optimize_image(img, fmt, quality, resize, width, height, lock_aspect)

            base = os.path.splitext(f.filename)[0]
            out_name = f"{base}.{fmt}"
            zf.writestr(out_name, optimized)

            results.append(
                {
                    "filename": out_name,
                    "original_size": original_size,
                    "optimized_size": len(optimized),
                }
            )

    if not results:
        return jsonify({"error": "No valid images could be processed"}), 400

    zip_buf.seek(0)

    response = send_file(
        zip_buf,
        mimetype="application/zip",
        as_attachment=True,
        download_name="optimized.zip",
    )
    # Embed results as a response header so the frontend can read them
    import json, base64
    response.headers["X-Results"] = base64.b64encode(
        json.dumps(results).encode()
    ).decode()
    return response


def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    if "--no-browser" not in sys.argv:
        threading.Timer(1.0, open_browser).start()
    app.run(debug=True, port=5000)
