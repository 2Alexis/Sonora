"""Client MusicBrainz.

Points clés respectés (règles de qualité du cahier des charges) :
- User-Agent identifiable OBLIGATOIRE (sinon MusicBrainz bloque avec un 403).
- Rate limiting : 1 requête / seconde max -> on sérialise les appels avec un verrou
  et on attend l'intervalle minimum entre deux requêtes.
- Gestion des erreurs : retries avec backoff sur 429 / 503, exceptions typées.
- fmt=json partout.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger("sonora.musicbrainz")


class MusicBrainzError(Exception):
    """Erreur générique côté MusicBrainz (réseau, statut HTTP, parsing)."""


class MusicBrainzClient:
    """Client synchrone, rate-limité et thread-safe pour l'API MusicBrainz."""

    def __init__(self) -> None:
        self._base_url = settings.musicbrainz_base_url.rstrip("/")
        self._headers = {
            "User-Agent": settings.musicbrainz_user_agent,
            "Accept": "application/json",
        }
        self._min_interval = settings.musicbrainz_rate_limit_seconds
        self._lock = threading.Lock()
        self._last_request_ts = 0.0
        self._client = httpx.Client(
            headers=self._headers,
            timeout=settings.musicbrainz_timeout_seconds,
        )

    # ------------------------------------------------------------------ #
    # Bas niveau : requête HTTP rate-limitée + retries
    # ------------------------------------------------------------------ #
    def _throttle(self) -> None:
        """Bloque jusqu'à ce que l'intervalle minimum soit respecté."""
        with self._lock:
            elapsed = time.monotonic() - self._last_request_ts
            wait = self._min_interval - elapsed
            if wait > 0:
                time.sleep(wait)
            self._last_request_ts = time.monotonic()

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        params = {**params, "fmt": "json"}
        url = f"{self._base_url}/{path.lstrip('/')}"
        last_exc: Exception | None = None

        for attempt in range(1, settings.musicbrainz_max_retries + 1):
            self._throttle()
            try:
                resp = self._client.get(url, params=params)
            except httpx.HTTPError as exc:
                last_exc = exc
                logger.warning("Erreur réseau MusicBrainz (tentative %d) : %s", attempt, exc)
                time.sleep(self._min_interval * attempt)
                continue

            if resp.status_code == 200:
                try:
                    return resp.json()
                except ValueError as exc:  # réponse non-JSON
                    raise MusicBrainzError("Réponse MusicBrainz non-JSON") from exc

            if resp.status_code in (429, 503):
                # Rate limit dépassé / service occupé -> backoff et retry
                logger.warning(
                    "MusicBrainz %s (tentative %d), backoff…", resp.status_code, attempt
                )
                time.sleep(self._min_interval * (attempt + 1))
                continue

            if resp.status_code == 404:
                raise MusicBrainzError(f"Ressource introuvable : {path}")

            raise MusicBrainzError(
                f"MusicBrainz a répondu {resp.status_code} pour {path}"
            )

        raise MusicBrainzError(
            f"Échec après {settings.musicbrainz_max_retries} tentatives : {path}"
        ) from last_exc

    # ------------------------------------------------------------------ #
    # Haut niveau : endpoints métier
    # ------------------------------------------------------------------ #
    def search_artists(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Recherche d'artistes par nom. Retourne la liste brute des résultats."""
        data = self._get("artist", {"query": query, "limit": limit})
        return data.get("artists", [])

    def get_artist(self, mbid: str) -> dict[str, Any]:
        """Lookup complet d'un artiste (genres, area, relations)."""
        # NB : `area` n'est PAS un `inc` valide pour un artiste (l'area est
        # renvoyée par défaut dans la réponse). L'inclure provoque un HTTP 400.
        return self._get(
            f"artist/{mbid}",
            {"inc": "genres+aliases+artist-rels+url-rels"},
        )

    def browse_recordings(self, artist_mbid: str, limit: int = 25) -> list[dict[str, Any]]:
        """Récupère les enregistrements d'un artiste avec crédits + releases.

        On utilise l'endpoint de RECHERCHE (`query=arid:<mbid>`) plutôt que le
        browse : lui seul renvoie à la fois `artist-credit` (indispensable à la
        détection de collaborations) ET `releases` embarquées (rattachement aux
        albums). Le browse refuse `inc=releases` (HTTP 400).
        """
        data = self._get(
            "recording",
            {
                "query": f"arid:{artist_mbid}",
                "limit": min(limit, 100),  # MusicBrainz plafonne à 100
            },
        )
        return data.get("recordings", [])

    def get_release(self, mbid: str) -> dict[str, Any]:
        """Lookup d'une release avec labels et area."""
        return self._get(
            f"release/{mbid}",
            {"inc": "labels+release-groups+artist-credits"},
        )

    def close(self) -> None:
        self._client.close()


# Singleton partagé (garantit un rate-limiter global commun à tous les appels).
_client: MusicBrainzClient | None = None


def get_musicbrainz_client() -> MusicBrainzClient:
    global _client
    if _client is None:
        _client = MusicBrainzClient()
    return _client
