from datetime import datetime
from flask import Blueprint, render_template, request, redirect, abort, flash, session

from database import db
from models import Review, Music
from access_control import check_session

reviews_bp = Blueprint("reviews", __name__)

@reviews_bp.before_request
@check_session
def _protect_reviews():
    pass

def get_r_or_404(r_id: int) -> Review:
    q = Review.query.filter_by(id=r_id)
    if session["user"]["role"] != "admin":
        q = q.filter_by(user_id=session["user"]["id"])
    r = q.first()
    if not r:
        abort(404)
    return r

@reviews_bp.url_value_preprocessor
def autoload_review(endpoint, values):
    if values and "r_id" in values:
        values["r"] = get_r_or_404(values["r_id"])

def _parse_int(value, field_name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} inválido")

def _parse_rating(value) -> int:
    if value is None:
        return 3
    s = str(value).strip()
    if not s:
        return 3
    if "★" in s:
        return s.count("★")
    try:
        return int(s)
    except ValueError:
        raise ValueError("Valoración inválida")

def _parse_date(value: str):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise ValueError("Fecha inválida (usa YYYY-MM-DD)")

def _valid_rating(v: int) -> bool:
    return 1 <= v <= 5

@reviews_bp.route("/", methods=["GET"])
def reviews_list():
    q = Review.query
    if session["user"]["role"] != "admin":
        q = q.filter(Review.user_id == session["user"]["id"])
    reviews = q.order_by(Review.id.asc()).all()

    music_list = Music.query.order_by(Music.id.asc()).all()
    music_by_id = {m.id: m for m in music_list}
    return render_template("reviews/review.html", reviews=reviews, music_by_id=music_by_id)

@reviews_bp.route("/new", methods=["GET"])
def reviews_new():
    music_list = Music.query.order_by(Music.id.asc()).all()
    return render_template("reviews/new_rev.html", music=music_list)

@reviews_bp.route("/", methods=["POST"])
def reviews_create():
    try:
        music_id = _parse_int(request.form.get("music_id"), "Música")
        fecha = _parse_date(request.form.get("fecha"))
        valoracion = _parse_rating(request.form.get("valoracion"))
    except ValueError as e:
        flash(str(e), "error")
        return redirect(request.referrer or "/reviews/new")

    texto = (request.form.get("texto") or "").strip()

    if not texto:
        flash("La reseña no puede estar vacía", "error")
        return redirect(request.referrer or "/reviews/new")

    if not _valid_rating(valoracion):
        flash("La valoración debe estar entre 1 y 5", "error")
        return redirect(request.referrer or "/reviews/new")

    m = Music.query.get(music_id)
    if not m:
        flash("La música no es válida", "error")
        return redirect(request.referrer or "/reviews/new")

    user_id = session["user"]["id"]

    exists = Review.query.filter_by(user_id=user_id, music_id=m.id, fecha=fecha).first()
    if exists:
        flash("Ya existe una reseña para esa música en esa fecha", "error")
        return redirect("/reviews/")

    r = Review(
        user_id=user_id,
        music_id=m.id,
        fecha=fecha,
        valoracion=valoracion,
        texto=texto,
    )

    db.session.add(r)
    db.session.commit()
    flash("Reseña creada", "success")
    return redirect("/reviews/")

@reviews_bp.route("/<int:r_id>/edit", methods=["GET"])
def reviews_edit(r_id, r):
    music_list = Music.query.order_by(Music.id.asc()).all()
    return render_template("reviews/edit_rev.html", r=r, music=music_list)

@reviews_bp.route("/<int:r_id>", methods=["PUT"])
def reviews_update(r_id, r):
    try:
        music_id = _parse_int(request.form.get("music_id"), "Música")
        fecha = _parse_date(request.form.get("fecha"))
        valoracion = _parse_rating(request.form.get("valoracion"))
    except ValueError as e:
        flash(str(e), "error")
        return redirect(f"/reviews/{r_id}/edit")

    texto = (request.form.get("texto") or "").strip()

    if not texto:
        flash("La reseña no puede estar vacía", "error")
        return redirect(f"/reviews/{r_id}/edit")

    if not _valid_rating(valoracion):
        flash("La valoración debe estar entre 1 y 5", "error")
        return redirect(f"/reviews/{r_id}/edit")

    if not Music.query.get(music_id):
        flash("La música no es válida", "error")
        return redirect(f"/reviews/{r_id}/edit")

    r.music_id = music_id
    r.fecha = fecha
    r.valoracion = valoracion
    r.texto = texto

    db.session.commit()
    flash("Reseña editada", "success")
    return redirect("/reviews/")

@reviews_bp.route("/<int:r_id>", methods=["DELETE"])
def reviews_delete(r_id, r):
    db.session.delete(r)
    db.session.commit()
    flash("Reseña borrada", "success")
    return redirect("/reviews/")