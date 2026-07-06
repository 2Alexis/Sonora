"""Endpoints de recherche d'artistes (via MusicBrainz)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.clients.musicbrainz import MusicBrainzError
from app.models.schemas import ArtistSearchResult
from app.services import search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/artists", response_model=list[ArtistSearchResult])
def search_artists(
    q: str = Query(..., min_length=1, description="Nom d'artiste à rechercher"),
    limit: int = Query(10, ge=1, le=25),
):
    """Recherche des artistes sur MusicBrainz par nom."""
    try:
        return search_service.search_artists(q, limit=limit)
    except MusicBrainzError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
