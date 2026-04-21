import asyncio
import httpx

URL_BASE = "http://127.0.0.1:5000"
URL_BASE_API = f"{URL_BASE}/api/v1"


async def get_music():
    url_music = f"{URL_BASE_API}/music/"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url_music)
            response.raise_for_status()
            music = response.json()
            print("Lista de música recuperada con éxito.")
            print(music)
            return music
        except httpx.HTTPStatusError as exc:
            print(f"Error del servidor ({exc.response.status_code}) al pedir música.")
            try:
                print(exc.response.json())
            except Exception:
                print(exc.response.text)
        except httpx.RequestError as exc:
            print(f"Error de red conectando a {exc.request.url}")


async def get_music_by_id(music_id: int = 1):
    url_music = f"{URL_BASE_API}/music/{music_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url_music)
            response.raise_for_status()
            music = response.json()
            print(f"Música {music_id} recuperada con éxito.")
            print(music)
            return music
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                print(f"La música con ID {music_id} no existe en la base de datos.")
            else:
                print(f"Error HTTP {exc.response.status_code}.")
                try:
                    print(exc.response.json())
                except Exception:
                    print(exc.response.text)
        except httpx.RequestError as exc:
            print(f"Error de red: {exc}")


async def create_music(new_music: dict):
    url_music = f"{URL_BASE_API}/music/"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url_music, json=new_music)
            response.raise_for_status()
            music = response.json()
            print("Nueva música creada correctamente.")
            print(music)
            return music
        except httpx.HTTPStatusError as exc:
            print(f"Error al crear música ({exc.response.status_code}).")
            try:
                print(f"Detalle del servidor: {exc.response.json()}")
            except Exception:
                print(f"Detalle bruto: {exc.response.text}")
        except httpx.RequestError as exc:
            print(f"Error de red: {exc}")


async def update_music(music_id: int, changes: dict):
    url_music = f"{URL_BASE_API}/music/{music_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url_music, json=changes)
            response.raise_for_status()
            music = response.json()
            print(f"Música {music_id} actualizada correctamente.")
            print(music)
            return music
        except httpx.HTTPStatusError as exc:
            print(f"Error al actualizar música ({exc.response.status_code}).")
            try:
                print(exc.response.json())
            except Exception:
                print(exc.response.text)
        except httpx.RequestError as exc:
            print(f"Error de red: {exc}")


async def delete_music(music_id: int):
    url_music = f"{URL_BASE_API}/music/{music_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url_music)
            response.raise_for_status()
            print(f"Música {music_id} eliminada correctamente.")
            print(response.json())
            return response.json()
        except httpx.HTTPStatusError as exc:
            print(f"Error al borrar música ({exc.response.status_code}).")
            try:
                print(exc.response.json())
            except Exception:
                print(exc.response.text)
        except httpx.RequestError as exc:
            print(f"Error de red: {exc}")


async def main():
    print("--- Listando toda la música ---")
    music_list = await get_music()

    music_existente_id = None
    if music_list and len(music_list) > 0:
        music_existente_id = music_list[0]["id"]

    if music_existente_id is not None:
        print("\n--- Consultando una música existente ---")
        existing_music = await get_music_by_id(music_existente_id)
    else:
        print("\nNo hay música existente para probar GET by ID.")
        return

    print("\n--- Consultando una música que no existe (prueba de error) ---")
    await get_music_by_id(9999)

    user_id = existing_music["user_id"]

    print(f"\n--- Usando user_id existente: {user_id} ---")

    print("\n--- Creando una música nueva ---")
    nueva_music = {
        "tipo": "Canción",
        "nombre": "Prueba API",
        "artista": "Marta",
        "genero": "Pop",
        "duracion": "03:15",
        "año": 2026,
        "url": "https://example.com",
        "user_id": user_id
    }

    created = await create_music(nueva_music)

    if created and "id" in created:
        music_id = created["id"]

        print("\n--- Consultando la música recién creada ---")
        await get_music_by_id(music_id)

        print("\n--- Actualizando la música recién creada ---")
        cambios = {
            "nombre": "Prueba API Actualizada",
            "genero": "Rock",
            "año": 2025
        }
        await update_music(music_id, cambios)

        print("\n--- Borrando la música creada ---")
        await delete_music(music_id)
    else:
        print("\nNo se pudo crear la música, así que no se harán PUT ni DELETE.")


if __name__ == "__main__":
    asyncio.run(main())