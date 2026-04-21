from flask import Blueprint, render_template, request, redirect, abort, flash, current_app, session
import os

from database import db
from models import Music
from handle_files import save_file, delete_file
from access_control import check_session

music_bp = Blueprint("music", __name__)

TIPOS = ["Canción", "Álbum"]

@music_bp.before_request
@check_session
def _protect_music():
    pass

def get_m_or_404(m_id: int) -> Music:
    q = Music.query.filter_by(id=m_id)
    if session["user"]["role"] != "admin":
        q = q.filter_by(user_id=session["user"]["id"])
    m = q.first()
    if not m:
        abort(404)
    return m

@music_bp.url_value_preprocessor
def autoload_music(endpoint, values):
    if values and "m_id" in values:
        values["m"] = get_m_or_404(values["m_id"])

def _bad_name(name: str) -> bool:
    bad_chars = ["(", ")", "/", "=", "<", ">", "{", "}", ";"]
    return any(c in (name or "") for c in bad_chars)

def _valid_duration(d: str) -> bool:
    if not d:
        return False

    parts = d.split(":")

    if len(parts) == 2:
        mm, ss = parts
        if not (mm.isdigit() and ss.isdigit()):
            return False
        return 0 <= int(ss) <= 59

    if len(parts) == 3:
        hh, mm, ss = parts
        if not (hh.isdigit() and mm.isdigit() and ss.isdigit()):
            return False
        return 0 <= int(mm) <= 59 and 0 <= int(ss) <= 59

    return False

@music_bp.route("/", methods=["GET"])
def music_list():
    q_txt = (request.args.get("q") or "").strip()
    tipo_filter = (request.args.get("tipo") or "").strip()
    genero_filter = (request.args.get("genero") or "").strip()

    q = Music.query

    if session["user"]["role"] != "admin":
        q = q.filter(Music.user_id == session["user"]["id"])

    if q_txt:
        like = f"%{q_txt}%"
        q = q.filter((Music.nombre.ilike(like)) | (Music.artista.ilike(like)))

    if tipo_filter:
        q = q.filter(Music.tipo == tipo_filter)

    if genero_filter:
        q = q.filter(Music.genero == genero_filter)

    filtered = q.order_by(Music.id.asc()).all()

    generos_q = db.session.query(Music.genero).filter(Music.genero.isnot(None))
    if session["user"]["role"] != "admin":
        generos_q = generos_q.filter(Music.user_id == session["user"]["id"])

    generos = [
        row[0]
        for row in generos_q.distinct().order_by(Music.genero.asc()).all()
        if row[0]
    ]

    return render_template("music/list.html", music=filtered, generos=generos)

@music_bp.route("/new", methods=["GET"])
def music_new():
    return render_template("music/new.html", tipo=TIPOS)

@music_bp.route("/", methods=["POST"])
@save_file
def music_create(filename=None):
    tipo_val = (request.form.get("tipo") or "").strip()
    nombre = (request.form.get("nombre") or "").strip()
    artista = (request.form.get("artista") or "").strip()
    genero = (request.form.get("genero") or "").strip()
    duracion = (request.form.get("duracion") or "").strip()
    url = (request.form.get("url") or "").strip()
    año_raw = request.form.get("año")

    if _bad_name(nombre):
        flash("El nombre no es valido", "error")
        return redirect("/music/new")

    if not _valid_duration(duracion):
        flash("La duracion no es valida", "error")
        return redirect("/music/new")

    if tipo_val not in TIPOS:
        flash("El tipo no es valido", "error")
        return redirect("/music/new")

    try:
        año_int = int(año_raw)
    except (TypeError, ValueError):
        flash("Año inválido.", "error")
        return redirect("/music/new")

    album = (request.form.get("album") or "").strip()
    num_canciones_raw = request.form.get("numCanciones") or request.form.get("num_canciones")

    if tipo_val == "Canción":
        album_final = album or "Single"
        num_canciones_final = None
    else:
        album_final = None
        try:
            num_canciones_final = int(num_canciones_raw or 1)
            if num_canciones_final < 1:
                flash("El numero de canciones no es valido", "error")
                return redirect("/music/new")
        except (TypeError, ValueError):
            flash("El numero de canciones no es valido", "error")
            return redirect("/music/new")

    item = Music(
        tipo=tipo_val,
        imagen=filename,
        nombre=nombre,
        artista=artista,
        genero=genero,
        album=album_final,
        num_canciones=num_canciones_final,
        duracion=duracion,
        año=año_int,
        url=url,
        user_id=session["user"]["id"],
    )

    db.session.add(item)
    db.session.commit()

    flash("Música creada", "success")
    return redirect("/music/")

@music_bp.route("/<int:m_id>", methods=["GET"])
def music_show(m_id, m):
    return render_template("music/show.html", m=m)

@music_bp.route("/<int:m_id>/edit", methods=["GET"])
def music_edit(m_id, m):
    return render_template("music/edit.html", m=m, tipo=TIPOS)

@music_bp.route("/<int:m_id>", methods=["PUT"])
@save_file
def music_update(m_id, m, filename=None):
    tipo_val = (request.form.get("tipo") or "").strip()
    nombre = (request.form.get("nombre") or "").strip()
    artista = (request.form.get("artista") or "").strip()
    genero = (request.form.get("genero") or "").strip()
    duracion = (request.form.get("duracion") or "").strip()
    url = (request.form.get("url") or "").strip()
    año_raw = request.form.get("año")

    if _bad_name(nombre):
        flash("El nombre no es valido", "error")
        return redirect(f"/music/{m_id}/edit")

    if not _valid_duration(duracion):
        flash("La duracion no es valida", "error")
        return redirect(f"/music/{m_id}/edit")

    if tipo_val not in TIPOS:
        flash("El tipo no es valido", "error")
        return redirect(f"/music/{m_id}/edit")

    try:
        año_int = int(año_raw)
    except (TypeError, ValueError):
        flash("El año no es valido", "error")
        return redirect(f"/music/{m_id}/edit")

    album = (request.form.get("album") or "").strip()
    num_canciones_raw = request.form.get("numCanciones") or request.form.get("num_canciones")

    if tipo_val == "Canción":
        album_final = album or "Single"
        num_canciones_final = None
    else:
        album_final = None
        try:
            num_canciones_final = int(num_canciones_raw or 1)
            if num_canciones_final < 1:
                flash("El numero de canciones no es valido", "error")
                return redirect(f"/music/{m_id}/edit")
        except (TypeError, ValueError):
            flash("El numero de canciones no es valido", "error")
            return redirect(f"/music/{m_id}/edit")

    m.tipo = tipo_val
    m.nombre = nombre
    m.artista = artista
    m.genero = genero
    m.album = album_final
    m.num_canciones = num_canciones_final
    m.duracion = duracion
    m.año = año_int
    m.url = url

    if filename:
        old_image = getattr(m, "imagen", None)
        if old_image and not str(old_image).startswith("/public/"):
            old_big = os.path.join(current_app.config["UPLOAD_FOLDER"], old_image)
            old_thumb = os.path.join(current_app.config["UPLOAD_FOLDER"], "thumbnails", old_image)
            for p in (old_thumb, old_big):
                try:
                    os.remove(p)
                except FileNotFoundError:
                    pass
        m.imagen = filename

    db.session.commit()
    flash("Música editada", "success")
    return redirect("/music/")

@music_bp.route("/<int:m_id>", methods=["DELETE"])
@delete_file
def music_delete(m_id, m):
    db.session.delete(m)
    db.session.commit()
    flash("Música borrada", "success")
    return redirect("/music/")