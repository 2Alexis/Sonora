"""Client Last.fm (nécessite une clé API gratuite).

Enrichit avec :
- artistes similaires (+ score de correspondance) -> relations SIMILAR_TO,
- nombre d'auditeurs / lectures -> popularité réelle,
- tags -> genres complémentaires.

Si `LASTFM_API_KEY` n'est pas défini, le client est DÉSACTIVÉ silencieusement :
l'application continue de fonctionner avec MusicBrainz + Deezer seuls.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger("sonora.lastfm")


class LastfmClient:
    def __init__(self) -> None:
        self._key = settings.lastfm_api_key
        self._base = settings.lastfm_base_url.rstrip("/")
        self._min_interval = settings.lastfm_rate_limit_seconds
        self._lock = threading.Lock()
        self._last = 0.0
        self._client = httpx.Client(
            headers={"User-Agent": settings.musicbrainz_user_agent},
            timeout=settings.lastfm_timeout_seconds,
        )

    @property
    def enabled(self) -> bool:
        return bool(self._key)

    def _throttle(self) -> None:
        with self._lock:
            wait = self._min_interval - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()

    def _get(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {}
        self._throttle()
        query = {**params, "method": method, "api_key": self._key, "format": "json"}
        try:
            resp = self._client.get(self._base, params=query)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            logger.warning("Last.fm indisponible (%s) : %s", method, exc)
            return {}
        if isinstance(data, dict) and data.get("error"):
            logger.warning("Last.fm error (%s) : %s", method, data.get("message"))
            return {}
        return data

    # ------------------------------------------------------------------ #
    def similar_artists(self, name: str, limit: int = 20) -> list[dict[str, Any]]:
        """Artistes similaires avec score `match` (0..1)."""
        data = self._get("artist.getsimilar", {"artist": name, "limit": limit, "autocorrect": 1})
        return (data.get("similarartists") or {}).get("artist") or []

    def artist_info(self, name: str) -> dict[str, Any]:
        """Statistiques (listeners, playcount) + tags d'un artiste."""
        data = self._get("artist.getinfo", {"artist": name, "autocorrect": 1})
        return data.get("artist") or {}

    def close(self) -> None:
        self._client.close()


_client: LastfmClient | None = None


def get_lastfm_client() -> LastfmClient:
    global _client
    if _client is None:
        _client = LastfmClient()
    return _client
