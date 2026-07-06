"""Recherche d'artistes via MusicBrainz (normalisée pour le frontend)."""
from __future__ import annotations

from app.clients.musicbrainz import get_musicbrainz_client
from app.models.schemas import ArtistSearchResult


def search_artists(query: str, limit: int = 10) -> list[ArtistSearchResult]:
    client = get_musicbrainz_client()
    raw = client.search_artists(query, limit=limit)
    results: list[ArtistSearchResult] = []
    for item in raw:
        life = item.get("life-span", {}) or {}
        results.append(
            ArtistSearchResult(
                mbid=item.get("id"),
                name=item.get("name") or "Unknown",
                type=item.get("type"),
                country=item.get("country") or item.get("area", {}).get("name"),
                begin_date=life.get("begin"),
                disambiguation=item.get("disambiguation"),
                score=item.get("score"),
            )
        )
    return results
