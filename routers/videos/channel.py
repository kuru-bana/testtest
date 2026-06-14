import asyncio

import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from core import get_client, get_instances

router = APIRouter()

# ── Channel home ──────────────────────────────────────────────────────────────

_CHANNEL_HOME_BASE = "https://choco-youtube-js.onrender.com"


@router.get("/api/channel-home/{channel_id}")
async def api_channel_home(channel_id: str):
    try:
        client = await get_client()
        resp = await client.get(f"{_CHANNEL_HOME_BASE}/channel/{channel_id}", timeout=15)
        resp.raise_for_status()
        return JSONResponse(resp.json())
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=502)


# ── Instances list ────────────────────────────────────────────────────────────

@router.get("/api/instances")
async def api_instances():
    categories = [
        "video", "search", "trending", "trending_music", "trending_gaming",
        "trending_news", "trending_movies", "channel", "channel_videos",
        "channel_shorts", "channel_streams", "channel_latest", "channel_playlists",
        "channel_comments", "channel_search", "playlist", "mix", "hashtag",
        "comments", "transcripts", "captions", "annotations", "clip",
        "resolveurl", "popular", "stats", "search_suggestions", "search_filters",
    ]
    results = await asyncio.gather(
        *[get_instances(cat) for cat in categories],
        return_exceptions=True,
    )
    all_instances = {
        cat: result
        for cat, result in zip(categories, results)
        if not isinstance(result, Exception)
    }
    return JSONResponse({"all": all_instances})
