from flask import Blueprint, render_template, request, redirect, session, flash
from database import db
from models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET"])
def register_view():
    return render_template("auth/register.html")

@auth_bp.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not username or not email or not password:
        flash("Faltan campos", "error")
        return redirect("/auth/register")

    if User.query.filter_by(email=email).first():
        flash("Ese email ya está registrado", "error")
        return redirect("/auth/register")

    user = User(username=username, email=email, role="user")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    flash("Cuenta registrada, inicia sesion para continuar", "success")
    return redirect("/auth/login")

@auth_bp.route("/login", methods=["GET"])
def login_view():
    return render_template("auth/login.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        session["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }
        flash("Sesion iniciada", "success")
        return redirect("/")
    flash("Email o contraseña incorrectos", "error")
    return redirect("/auth/login")

@auth_bp.route("/logout", methods=["GET"])
def logout():
    session.pop("user", None)
    flash("Sesión cerrada", "success")
    return redirect("/")