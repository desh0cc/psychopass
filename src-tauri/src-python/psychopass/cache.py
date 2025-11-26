import os, hashlib, aiohttp, asyncio
from typing import Optional, List

class Cache:
    def __init__(self, cache_path: str):
        self.cache_path = cache_path
        os.makedirs(self.cache_path, exist_ok=True)

        self.semaphore = asyncio.Semaphore(20)

    async def cache_media(self, media: Optional[str]) -> Optional[str]:
        """Cache a single file or URL asynchronously"""
        if not media:
            return None

        content = await self._load_content(media)
        if content is None:
            return None

        return self._save_to_cache(content)

    async def cache_media_batch(self, media_list: List[str]) -> List[Optional[str]]:
        """
        Caches multiple files asynchronously.
        Keeps order identical to the input list.
        """

        tasks = [
            asyncio.create_task(self.cache_media(media))
            for media in media_list
        ]

        return await asyncio.gather(*tasks)

    async def _load_content(self, media: str) -> Optional[bytes]:
        if media.startswith("http"):
            return await self._download(media)
        return await self._read_file(media)

    async def _download(self, url: str) -> Optional[bytes]:
        async with self.semaphore:  # limit concurrency
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        headers={"User-Agent": "Mozilla/5.0"}
                    ) as resp:
                        if resp.status != 200:
                            print(f"[ERROR] HTTP {resp.status}: {url}")
                            return None
                        return await resp.read()
            except Exception as e:
                print(f"[ERROR] Failed to download {url}: {e}")
                return None

    async def _read_file(self, filepath: str) -> Optional[bytes]:
        try:
            # Local file IO must be run in a thread to not block the event loop
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: open(filepath, "rb").read())
        except Exception as e:
            print(f"[ERROR] Failed to read {filepath}: {e}")
            return None

    def _save_to_cache(self, content: bytes) -> str:
        """Save content to cache directory using MD5 hash"""
        hashname = hashlib.md5(content).hexdigest()
        cached_path = os.path.join(self.cache_path, hashname)

        if not os.path.exists(cached_path):
            # atomic write
            tmp_path = cached_path + ".tmp"
            with open(tmp_path, "wb") as f:
                f.write(content)
            os.replace(tmp_path, cached_path)

        return cached_path
