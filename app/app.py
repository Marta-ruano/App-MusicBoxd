from flask import Flask, render_template, send_from_directory
import os
import logging
import click

import blueprints
from methodOverride import MethodOverrideMiddleware
from flask_migrate import Migrate
from flask.cli import with_appcontext
from flasgger import Swagger
from sqlalchemy_utils import create_database, database_exists

from database import db
from models import Music
from logger import logger

migrate = Migrate()

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="public",
    static_url_path="/public"
)

app.secret_key = str(os.environ.get("SECRET_KEY") or "1234")

app.config["SWAGGER"] = {
    "title": "MusicBoxd API",
    "uiversion": 3,
    "openapi": "3.0.3"
}

swagger = Swagger(app, template_file="openapi.yaml")

app.logger.handlers.clear()
for handler in logger.handlers:
    app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.handlers.clear()
for handler in logger.handlers:
    werkzeug_logger.addHandler(handler)
werkzeug_logger.setLevel(logging.INFO)

app.wsgi_app = MethodOverrideMiddleware(app.wsgi_app)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:2011@localhost/MusicBoxd"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
    create_database(app.config["SQLALCHEMY_DATABASE_URI"])

migrate.init_app(app, db)

app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "assets", "images")
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg"}

app.register_blueprint(blueprints.auth_bp, url_prefix="/auth")
app.register_blueprint(blueprints.music_bp, url_prefix="/music")
app.register_blueprint(blueprints.reviews_bp, url_prefix="/reviews")
app.register_blueprint(blueprints.users_bp, url_prefix="/users")
app.register_blueprint(blueprints.api_v1_bp, url_prefix="/api/v1/music")


@click.command(name="seed")
@with_appcontext
def seed():
    from models.seeders import fillUser, fillMusic, fillReview
    fillUser()
    fillMusic()
    fillReview()


app.cli.add_command(seed)


@app.route("/")
def home():
    canciones = (
        Music.query
        .filter(Music.tipo == "Canción")
        .order_by(Music.id.asc())
        .limit(3)
        .all()
    )

    albums = (
        Music.query
        .filter(Music.tipo == "Álbum")
        .order_by(Music.id.asc())
        .limit(3)
        .all()
    )

    return render_template("index.html", canciones=canciones, albums=albums)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(os.path.join(app.root_path, "assets", "images"), filename)


@app.errorhandler(404)
def not_found(e):
    return render_template("error404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error500.html"), 500


@app.get("/thumbnails/<path:filename>")
def thumbnails(filename):
    return send_from_directory(os.path.join(app.config["UPLOAD_FOLDER"], "thumbnails"), filename)


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(os.path.join(app.root_path, "assets"), filename)


if __name__ == "__main__":
    app.run(debug=True)