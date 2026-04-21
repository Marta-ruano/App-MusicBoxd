from flask import Blueprint, render_template, request, redirect, abort, flash
from werkzeug.security import generate_password_hash
from models import User, Music, Review
from database import db
from models import User
from access_control import check_session, require_role

users_bp = Blueprint("users", __name__)

@users_bp.before_request
@check_session
@require_role("admin")
def _protect_users():
    pass

def get_user_or_404(user_id: str) -> User:
    u = User.query.get(user_id)
    if not u:
        abort(404)
    return u

@users_bp.url_value_preprocessor
def autoload_user(endpoint, values):
    if values and "user_id" in values:
        values["u"] = get_user_or_404(values["user_id"])

def _bad_username(username: str) -> bool:
    bad_chars = [" ", "(", ")", "/", "=", "<", ">", "{", "}", ";"]
    return any(c in (username or "") for c in bad_chars)

@users_bp.route("/", methods=["GET"])
def users_list():
    users = User.query.order_by(User.id.asc()).all()
    return render_template("users/list_user.html", users=users)

@users_bp.route("/new", methods=["GET"])
def users_new():
    return render_template("users/new_user.html")

@users_bp.route("/", methods=["POST"])
def users_create():
    username = (request.form.get("username") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    password = (request.form.get("password") or "").strip()

    if not username or _bad_username(username):
        flash("El nombre no debe tener espacios ni caracteres raros", "error")
        return redirect(request.referrer or "/users/new")

    if not email or ("@" not in email) or ("." not in email):
        flash("El email debe contener @ y .", "error")
        return redirect(request.referrer or "/users/new")

    if not password or len(password) < 3:
        flash("La contraseña debe tener mínimo 3 caracteres", "error")
        return redirect(request.referrer or "/users/new")

    if User.query.filter_by(email=email).first():
        flash("Ya existe un usuario con ese email", "error")
        return redirect(request.referrer or "/users/new")

    if User.query.filter_by(username=username).first():
        flash("Ya existe un usuario con ese username", "error")
        return redirect(request.referrer or "/users/new")

    u = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role="user",
    )
    db.session.add(u)
    db.session.commit()

    flash("Usuario creado", "success")
    return redirect("/users/")

@users_bp.route("/<string:user_id>", methods=["GET"])
def users_show(user_id, u):
    return render_template("users/show_user.html", user=u)

@users_bp.route("/<string:user_id>/edit", methods=["GET"])
def users_edit(user_id, u):
    return render_template("users/edit_user.html", user=u)

@users_bp.route("/<string:user_id>", methods=["PUT"])
def users_update(user_id, u):
    username = (request.form.get("username") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    password = (request.form.get("password") or "").strip()

    if not username or _bad_username(username):
        flash("El nombre no debe tener espacios ni caracteres raros", "error")
        return redirect(f"/users/{user_id}/edit")

    if not email or ("@" not in email) or ("." not in email):
        flash("El email debe contener @ y .", "error")
        return redirect(f"/users/{user_id}/edit")

    if not password or len(password) < 3:
        flash("La contraseña debe tener mínimo 3 caracteres", "error")
        return redirect(f"/users/{user_id}/edit")

    email_exists = User.query.filter(User.email == email, User.id != u.id).first()
    if email_exists:
        flash("Ya existe un usuario con ese email", "error")
        return redirect(f"/users/{user_id}/edit")

    username_exists = User.query.filter(User.username == username, User.id != u.id).first()
    if username_exists:
        flash("Ya existe un usuario con ese username", "error")
        return redirect(f"/users/{user_id}/edit")

    u.username = username
    u.email = email
    u.password_hash = generate_password_hash(password)
    db.session.commit()

    flash("Usuario editado", "success")
    return redirect("/users/")

@users_bp.route("/<user_id>", methods=["POST", "DELETE"])
def users_delete(user_id, u=None):
    if request.method == "POST" and request.form.get("_method", "").upper() != "DELETE":
        return ("Method Not Allowed", 405)

    user = u if u is not None else User.query.get_or_404(user_id)

    admin = User.query.filter_by(email="marta@gmail.com").first()

    Music.query.filter(Music.user_id == user.id).update(
        {Music.user_id: admin.id},
        synchronize_session=False
    )

    Review.query.filter(Review.user_id == user.id).update(
        {Review.user_id: admin.id},
        synchronize_session=False
    )

    db.session.delete(user)
    db.session.commit()
    return redirect("/users/")