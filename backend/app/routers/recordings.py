"""Endpoints enregistrements (Recording)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.clients.deezer import get_deezer_client
from app.services import recording_service

router = APIRouter(prefix="/recordings", tags=["recordings"])


@router.get("/{mbid}/preview")
def get_recording_preview(mbid: str):
    """Redirige vers l'extrait audio 30s Deezer, avec une URL fraîche.

    Les URLs de preview Deezer contiennent un token qui expire : on résout donc
    l'URL à la demande (au moment de la lecture) plutôt que de la stocker.
    """
    track_id = recording_service.get_deezer_track_id(mbid)
    if not track_id:
        raise HTTPException(status_code=404, detail="Aucun extrait disponible")
    track = get_deezer_client().get_track(track_id)
    preview = track.get("preview")
    if not preview:
        raise HTTPException(status_code=404, detail="Extrait indisponible côté Deezer")
    # 302 : le lecteur <audio> suit la redirection et joue le mp3 directement.
    return RedirectResponse(url=preview, status_code=302)


@router.get("")
def list_recordings(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    return recording_service.list_recordings(limit=limit, offset=offset)


@router.get("/{mbid}")
def get_recording(mbid: str):
    rec = recording_service.get_recording(mbid)
    if rec is None:
        raise HTTPException(status_code=404, detail="Enregistrement non trouvé")
    return rec


@router.get("/{mbid}/artists")
def get_recording_artists(mbid: str):
    return recording_service.get_recording_artists(mbid)


@router.get("/{mbid}/releases")
def get_recording_releases(mbid: str):
    return recording_service.get_recording_releases(mbid)
