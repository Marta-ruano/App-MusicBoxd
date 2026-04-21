from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from database import db
from models import Music, User
from dto.music_dto import MusicDTO, NewMusicDTO, EditMusicDTO
from services.external_music_service import get_other_songs_by_artist
from logger import logger

api_v1_bp = Blueprint("api_v1_bp", __name__)

TIPOS = ["Canción", "Álbum"]


def error_response(status: int, message: str, details=None):
    payload = {"error": message}
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status


def valid_duration(d: str) -> bool:
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


@api_v1_bp.route("/", methods=["GET"])
def get_all_music():
    logger.info("GET /api/v1/music")

    music_list = Music.query.order_by(Music.id.asc()).all()

    dto_list = [
        MusicDTO.model_validate(m).model_dump(by_alias=True)
        for m in music_list
    ]

    return jsonify(dto_list), 200


@api_v1_bp.route("/<int:music_id>", methods=["GET"])
async def get_music_by_id(music_id):
    logger.info(f"GET /api/v1/music/{music_id}")

    music = Music.query.get(music_id)
    if music is None:
        logger.warning(f"Music {music_id} not found")
        return error_response(404, f"Music {music_id} not found")

    response_dto = MusicDTO.model_validate(music).model_dump(by_alias=True)

    user = User.query.get(music.user_id)
    user_data = None
    if user is not None:
        user_data = {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": str(user.role)
        }

    response_dto["user"] = user_data

    try:
        canciones = await get_other_songs_by_artist(music.artista, music.nombre)

        response_dto["otras_canciones"] = [
            {
                "title": c.get("track_name"),
                "artist": c.get("artist_name"),
                "album": c.get("collection_name"),
                "release_date": c.get("release_date"),
                "preview_url": c.get("preview_url"),
                "cover": c.get("artwork_url")
            }
            for c in canciones
        ]

        logger.info(f"Artist songs enrichment OK for music {music_id}")

    except Exception as e:
        logger.error(f"Artist songs API error for music {music_id}: {str(e)}")
        response_dto["otras_canciones"] = []

    return jsonify(response_dto), 200


@api_v1_bp.route("/", methods=["POST"])
def create_music():
    logger.info("POST /api/v1/music")

    body = request.get_json()
    if body is None:
        return error_response(400, "Body JSON requerido")

    try:
        dto = NewMusicDTO.model_validate(body)
    except ValidationError as e:
        return error_response(400, "Validation error", e.errors())

    if dto.tipo not in TIPOS:
        return error_response(400, "El tipo debe ser 'Canción' o 'Álbum'")

    if not valid_duration(dto.duracion):
        return error_response(400, "Duración inválida (MM:SS o HH:MM:SS)")

    user = User.query.get(dto.user_id)
    if user is None:
        return error_response(404, f"User {dto.user_id} not found")

    if dto.tipo == "Canción":
        album_final = dto.album or "Single"
        num_canciones_final = None
    else:
        album_final = None
        num_canciones_final = dto.num_canciones or 1

    model = Music(
        tipo=dto.tipo,
        nombre=dto.nombre,
        artista=dto.artista,
        genero=dto.genero,
        album=album_final,
        num_canciones=num_canciones_final,
        duracion=dto.duracion,
        año=dto.año,
        url=dto.url,
        imagen=dto.imagen,
        user_id=dto.user_id
    )

    db.session.add(model)
    db.session.commit()

    response_dto = MusicDTO.model_validate(model)
    return jsonify(response_dto.model_dump(by_alias=True)), 201


@api_v1_bp.route("/<int:music_id>", methods=["PUT"])
def update_music(music_id):
    logger.info(f"PUT /api/v1/music/{music_id}")

    body = request.get_json()
    if body is None:
        return error_response(400, "Body JSON requerido")

    music = Music.query.get(music_id)
    if music is None:
        return error_response(404, f"Music {music_id} not found")

    try:
        dto = EditMusicDTO.model_validate(body)
    except ValidationError as e:
        return error_response(400, "Validation error", e.errors())

    cambios = dto.model_dump(exclude_unset=True)

    if "tipo" in cambios and cambios["tipo"] not in TIPOS:
        return error_response(400, "Tipo inválido")

    if "duracion" in cambios and not valid_duration(cambios["duracion"]):
        return error_response(400, "Duración inválida")

    for field, value in cambios.items():
        setattr(music, field, value)

    db.session.commit()

    response_dto = MusicDTO.model_validate(music)
    return jsonify(response_dto.model_dump(by_alias=True)), 200


@api_v1_bp.route("/<int:music_id>", methods=["DELETE"])
def delete_music(music_id):
    logger.info(f"DELETE /api/v1/music/{music_id}")

    music = Music.query.get(music_id)
    if music is None:
        return error_response(404, f"Music {music_id} not found")

    db.session.delete(music)
    db.session.commit()

    return jsonify({"message": f"Music {music_id} deleted"}), 200