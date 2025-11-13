import asyncio
import re
from typing import Any, Dict, Optional, Tuple, Union

from yt_dlp import YoutubeDL

from AnnieXMedia.utils.downloader import yt_dlp_download
from AnnieXMedia.utils.formatters import seconds_to_min


_SC_RE = re.compile(r"^https?://(soundcloud\.com|on\.soundcloud\.com)/.+", re.I)


class SoundAPI:
    async def valid(self, link: str) -> bool:
        return bool(link and _SC_RE.match(link))

    async def _extract_info(self, url: str) -> Dict[str, Any]:
        def _run(u: str):
            opts = {
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "skip_download": True,
            }
            with YoutubeDL(opts) as ydl:
                return ydl.extract_info(u, download=False)

        loop = asyncio.get_running_loop()
        info = await loop.run_in_executor(None, _run, url)

        _type = str(info.get("_type", ""))
        if _type in ("url", "url_transparent") and info.get("url"):
            info = await loop.run_in_executor(None, _run, info["url"])

        return info

    async def download(self, url: str) -> Union[Tuple[Dict[str, Any], str], bool]:
        try:
            info = await self._extract_info(url)
        except Exception:
            return False

        if not info or info.get("_type") == "playlist":
            return False

        title = (info.get("title") or "SoundCloud").strip()
        try:
            duration_sec = int(info.get("duration") or 0)
        except Exception:
            duration_sec = 0

        uploader = info.get("uploader") or ""
        thumb = (
            info.get("thumbnail")
            or (info.get("thumbnails") or [{}])[0].get("url")
            or ""
        )

        out_path: Optional[str] = await yt_dlp_download(url, type="audio", title=title)
        if not out_path:
            return False

        details = {
            "title": title,
            "duration_sec": duration_sec,
            "duration_min": seconds_to_min(max(duration_sec, 0)),
            "uploader": uploader,
            "thumb": thumb,
            "filepath": out_path,
        }
        return details, out_path