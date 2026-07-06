"""Endpoint d'import d'artistes depuis MusicBrainz vers Neo4j."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.clients.musicbrainz import MusicBrainzError
from app.models.schemas import ImportArtistRequest, ImportSummary
from app.services import import_service

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/artists", response_model=ImportSummary, status_code=201)
def import_artist(payload: ImportArtistRequest):
    """Importe un artiste (et ses morceaux/albums/collabs) dans Neo4j.

    Idempotent : réimporter le même MBID met à jour le nœud existant sans doublon.
    """
    try:
        return import_service.import_artist(
            payload.mbid,
            include_recordings=payload.include_recordings,
            max_recordings=payload.max_recordings,
        )
    except MusicBrainzError as exc:
        raise HTTPException(status_code=502, detail=f"Erreur MusicBrainz : {exc}")
