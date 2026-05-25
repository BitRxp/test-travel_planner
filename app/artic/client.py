import httpx

from app.artic import cache as artic_cache
from app.artic.schemas import ArtworkData, ArtworkDetailResponse, ArtworkSearchResponse
from app.config import settings
from app.core.exceptions import ArticAPIError, ArtworkNotFound

ARTWORK_FIELDS = "id,title,image_id"


async def get_artwork(artwork_id: int) -> ArtworkData:
    cache_key = f"artwork:{artwork_id}"
    cached = artic_cache.get(cache_key)
    if cached:
        return ArtworkData(**cached)

    url = f"{settings.ARTIC_BASE_URL}/artworks/{artwork_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params={"fields": ARTWORK_FIELDS}, timeout=10.0)
    except httpx.TimeoutException:
        raise ArticAPIError("Art Institute of Chicago API timed out")
    except httpx.RequestError:
        raise ArticAPIError("Failed to connect to Art Institute of Chicago API")

    if response.status_code == 404:
        raise ArtworkNotFound(f"Artwork with id={artwork_id} not found")

    if response.status_code >= 500:
        raise ArticAPIError(f"Art Institute of Chicago API returned {response.status_code}")

    response.raise_for_status()

    parsed = ArtworkDetailResponse.model_validate(response.json())
    artic_cache.set(cache_key, parsed.data.model_dump())
    return parsed.data


async def search_artworks(q: str, limit: int = 10, offset: int = 0) -> ArtworkSearchResponse:
    cache_key = f"search:{q}:{limit}:{offset}"
    cached = artic_cache.get(cache_key)
    if cached:
        return ArtworkSearchResponse.model_validate(cached)

    url = f"{settings.ARTIC_BASE_URL}/artworks/search"
    params = {"q": q, "limit": limit, "offset": offset, "fields": ARTWORK_FIELDS}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
    except httpx.TimeoutException:
        raise ArticAPIError("Art Institute of Chicago API timed out")
    except httpx.RequestError:
        raise ArticAPIError("Failed to connect to Art Institute of Chicago API")

    if response.status_code >= 500:
        raise ArticAPIError(f"Art Institute of Chicago API returned {response.status_code}")

    response.raise_for_status()

    parsed = ArtworkSearchResponse.model_validate(response.json())
    artic_cache.set(cache_key, response.json())
    return parsed
