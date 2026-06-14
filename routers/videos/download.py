from urllib.parse import quote

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, StreamingResponse

from core import get_client

router = APIRouter()


@router.get("/download")
async def download(url: str = Query(...), filename: str = Query(default="download")):
    try:
        client = await get_client()
        req = client.build_request("GET", url)
        upstream = await client.send(req, stream=True)
        if not upstream.is_success:
            raise Exception(f"HTTP {upstream.status_code}")

        content_type = upstream.headers.get("content-type", "application/octet-stream")
        content_length = upstream.headers.get("content-length")

        response_headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename, safe='')}",
            "Content-Type": content_type,
        }
        if content_length:
            response_headers["Content-Length"] = content_length

        async def stream_body():
            async for chunk in upstream.aiter_bytes():
                yield chunk
            await upstream.aclose()

        return StreamingResponse(stream_body(), headers=response_headers)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=502)
