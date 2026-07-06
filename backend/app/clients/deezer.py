"""Client Deezer (API publique, sans authentification).

Sert à ENRICHIR les données MusicBrainz :
- image de l'artiste, nombre de fans (popularité réelle),
- artistes similaires -> relations SIMILAR_TO,
- extraits audio 30s + pochettes sur les morceaux.

Deezer limite ~50 requêtes / 5 s : on applique un petit throttle par prudence.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger("sonora.deezer")


class DeezerClient:
    def __init__(self) -> None:
        self._base = settings.deezer_base_url.rstrip("/")
        self._min_interval = settings.deezer_rate_limit_seconds
        self._lock = threading.Lock()
        self._last = 0.0
        self._client = httpx.Client(
            headers={"User-Agent": settings.musicbrainz_user_agent},
            timeout=settings.deezer_timeout_seconds,
        )

    def _throttle(self) -> None:
        with self._lock:
            wait = self._min_interval - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._throttle()
        try:
            resp = self._client.get(f"{self._base}/{path.lstrip('/')}", params=params or {})
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            logger.warning("Deezer indisponible pour %s : %s", path, exc)
            return {}
        # Deezer renvoie {"error": {...}} avec un HTTP 200 en cas d'erreur applicative.
        if isinstance(data, dict) and data.get("error"):
            logger.warning("Deezer error pour %s : %s", path, data["error"])
            return {}
        return data

    # ------------------------------------------------------------------ #
    def search_artist(self, name: str) -> dict[str, Any] | None:
        """Meilleur match Deezer pour un nom d'artiste."""
        data = self._get("search/artist", {"q": name, "limit": 1})
        results = data.get("data") or []
        return results[0] if results else None

    def related_artists(self, artist_id: int, limit: int = 20) -> list[dict[str, Any]]:
        """Artistes similaires selon Deezer (pour les relations SIMILAR_TO)."""
        data = self._get(f"artist/{artist_id}/related", {"limit": limit})
        return data.get("data") or []

    def top_tracks(self, artist_id: int, limit: int = 50) -> list[dict[str, Any]]:
        """Morceaux les plus populaires d'un artiste (avec preview + pochette)."""
        data = self._get(f"artist/{artist_id}/top", {"limit": limit})
        return data.get("data") or []

    def search_track(self, artist: str, title: str) -> dict[str, Any] | None:
        """Cherche un morceau précis (artiste + titre) pour récupérer sa preview.

        Utilisé en repli quand le titre n'est pas dans les top tracks de l'artiste,
        ce qui élargit fortement la couverture des extraits audio.
        """
        q = f'artist:"{artist}" track:"{title}"'
        data = self._get("search/track", {"q": q, "limit": 1})
        results = data.get("data") or []
        return results[0] if results else None

    def get_track(self, track_id: int) -> dict[str, Any]:
        """Détail d'un morceau Deezer. Renvoie notamment une URL `preview` FRAÎCHE.

        Indispensable car les URLs de preview contiennent un token qui expire :
        on les résout au moment de la lecture, pas au moment du seed.
        """
        return self._get(f"track/{track_id}")

    def close(self) -> None:
        self._client.close()


_client: DeezerClient | None = None


def get_deezer_client() -> DeezerClient:
    global _client
    if _client is None:
        _client = DeezerClient()
    return _client
