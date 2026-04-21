import httpx
from aiocache import cached, Cache
from aiocache.serializers import JsonSerializer


@cached(ttl=600, cache=Cache.MEMORY, serializer=JsonSerializer())
async def get_other_songs_by_artist(artist: str, exclude_track: str = ""):
    url = "https://itunes.apple.com/search"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            url,
            params={
                "term": artist,
                "limit": 25,
                "entity": "song"
            }
        )
        response.raise_for_status()
        data = response.json()

    if data.get("resultCount", 0) == 0:
        return []

    normalized_artist = artist.strip().lower()
    normalized_exclude = exclude_track.strip().lower()

    songs = []
    seen = set()

    for item in data["results"]:
        item_artist = (item.get("artistName") or "").strip().lower()
        item_track = (item.get("trackName") or "").strip().lower()

        if item_artist != normalized_artist:
            continue

        if item_track == normalized_exclude:
            continue

        if item_track in seen:
            continue

        seen.add(item_track)

        songs.append({
            "track_name": item.get("trackName"),
            "artist_name": item.get("artistName"),
            "collection_name": item.get("collectionName"),
            "release_date": item.get("releaseDate"),
            "preview_url": item.get("previewUrl"),
            "artwork_url": item.get("artworkUrl100")
        })

        if len(songs) == 5:
            break

    return songs