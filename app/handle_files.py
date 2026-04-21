import os
import uuid
from functools import wraps
from pathlib import Path
from flask import request, redirect, current_app, flash
from models import Music
from PIL import Image

THUMB_SIZE = (200, 200)

def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]
    )

def _assets_root() -> str:
    return os.path.dirname(current_app.config["UPLOAD_FOLDER"])

def _thumbs_dir() -> str:
    return os.path.join(_assets_root(), "thumbnails")

def _ensure_dirs() -> None:
    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(_thumbs_dir(), exist_ok=True)

def _make_thumbnail(big_path: str, thumb_path: str) -> None:
    with Image.open(big_path) as img:
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        img.thumbnail(THUMB_SIZE)
        img.save(thumb_path)

def save_file(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        file = request.files.get("imagen")
        filename = None

        if file and file.filename:
            if not allowed_file(file.filename):
                flash("La imagen subida no coincide con las extensiones permitidas.", "error")
                return redirect(request.referrer or "/music/")

            _ensure_dirs()

            ext = file.filename.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"

            upload_folder = current_app.config["UPLOAD_FOLDER"]
            big_path = os.path.join(upload_folder, filename)
            file.save(big_path)

            thumb_path = os.path.join(_thumbs_dir(), filename)
            try:
                _make_thumbnail(big_path, thumb_path)
            except Exception:
                if os.path.exists(big_path):
                    os.remove(big_path)
                flash("No se pudo procesar la imagen para generar el thumbnail.", "error")
                return redirect(request.referrer or "/music/")

        kwargs["filename"] = filename
        return view(*args, **kwargs)
    return wrapper

def delete_file(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        m_id = kwargs.get("m_id")
        m = Music.query.get_or_404(m_id)

        img_path = getattr(m, "imagen", None)

        if img_path and isinstance(img_path, str) and not img_path.startswith("/public/"):
            filename = os.path.basename(img_path)
            stem = Path(filename).stem

            upload = Path(current_app.config["UPLOAD_FOLDER"])
            candidates = [
                upload / filename,
                upload / "thumbnails",
                upload.parent / "thumbnails",
                Path(current_app.root_path) / "assets" / "images" / "thumbnails",
                Path(current_app.root_path) / "assets" / "thumbnails",
            ]

            if (upload / filename).exists():
                (upload / filename).unlink()

            for d in candidates:
                if d.is_dir():
                    for p in d.iterdir():
                        if p.is_file() and (stem in p.stem or stem in p.name):
                            p.unlink(missing_ok=True)

        kwargs["m"] = m
        return f(*args, **kwargs)

    return wrapper