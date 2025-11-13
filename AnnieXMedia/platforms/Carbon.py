import random
import asyncio
import time
from pathlib import Path
from typing import Optional

import aiohttp
from aiohttp import client_exceptions

class UnableToFetchCarbon(Exception):
    pass

themes = [
    "3024-night", "a11y-dark", "blackboard", "base16-dark", "base16-light",
    "cobalt", "duotone-dark", "dracula-pro", "hopscotch", "lucario",
    "material", "monokai", "nightowl", "nord", "oceanic-next", "one-light",
    "one-dark", "panda-syntax", "parasio-dark", "seti", "shades-of-purple",
    "solarized+dark", "solarized+light", "synthwave-84", "twilight",
    "verminal", "vscode", "yeti", "zenburn",
]

colour = [
    "#FF0000", "#FF5733", "#FFFF00", "#008000", "#0000FF", "#800080", "#A52A2A",
    "#FF00FF", "#D2B48C", "#00FFFF", "#808000", "#800000", "#30D5C8", "#00FF00",
    "#008080", "#4B0082", "#EE82EE", "#FFC0CB", "#000000", "#FFFFFF", "#808080",
]

class CarbonAPI:
    def __init__(self, cache_dir: str = "cache", timeout_s: int = 20):
        self.language = "auto"
        self.drop_shadow = True
        self.drop_shadow_blur = "68px"
        self.drop_shadow_offset = "20px"
        self.font_family = "JetBrains Mono"
        self.width_adjustment = True
        self.watermark = False

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._timeout = aiohttp.ClientTimeout(total=timeout_s)
        self._session: Optional[aiohttp.ClientSession] = None

    async def _session_get(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self._timeout,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "AnnieXMusic/CarbonClient",
                },
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def generate(self, text: str, user_id) -> str:
        if not text:
            raise UnableToFetchCarbon("Empty text.")
        if len(text) > 10000:
            raise UnableToFetchCarbon("Text too long (max 10k characters).")

        params = {
            "code": text,
            "backgroundColor": random.choice(colour),
            "theme": random.choice(themes),
            "dropShadow": self.drop_shadow,
            "dropShadowOffsetY": self.drop_shadow_offset,
            "dropShadowBlurRadius": self.drop_shadow_blur,
            "fontFamily": self.font_family,
            "language": self.language,
            "watermark": self.watermark,
            "widthAdjustment": self.width_adjustment,
        }

        url = "https://carbonara.solopov.dev/api/cook"
        session = await self._session_get()


        last_exc = None
        for _ in range(2):
            try:
                async with session.post(url, json=params) as resp:
                    if resp.status != 200:
                        body = await resp.text()
                        raise UnableToFetchCarbon(f"Carbon API error {resp.status}: {body[:200]}")
                    data = await resp.read()

                    filename = f"carbon_{user_id}_{int(time.time()*1000)}.jpg"
                    out = self.cache_dir / filename
                    out.write_bytes(data)
                    return str(out.resolve())
            except client_exceptions.ClientConnectorError as e:
                last_exc = e
            except asyncio.TimeoutError as e:
                last_exc = e
        raise UnableToFetchCarbon(f"Network error: {last_exc!r}")