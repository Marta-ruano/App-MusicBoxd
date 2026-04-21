from typing import Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class MusicDTO(BaseModel):
    id: int
    tipo: str
    nombre: str
    artista: str
    genero: str
    album: Optional[str] = None
    num_canciones: Optional[int] = Field(default=None, alias="numCanciones")
    duracion: str
    año: int
    url: Optional[str] = None
    imagen: Optional[str] = None
    user_id: Union[int, str]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class NewMusicDTO(BaseModel):
    tipo: str
    nombre: str
    artista: str
    genero: str
    album: Optional[str] = None
    num_canciones: Optional[int] = Field(default=None, alias="numCanciones")
    duracion: str
    año: int
    url: Optional[str] = None
    imagen: Optional[str] = None
    user_id: Union[int, str]

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True
    )


class EditMusicDTO(BaseModel):
    tipo: Optional[str] = None
    nombre: Optional[str] = None
    artista: Optional[str] = None
    genero: Optional[str] = None
    album: Optional[str] = None
    num_canciones: Optional[int] = Field(default=None, alias="numCanciones")
    duracion: Optional[str] = None
    año: Optional[int] = None
    url: Optional[str] = None
    imagen: Optional[str] = None

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True
    )