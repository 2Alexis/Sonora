"""Enrichissement des données MusicBrainz via Deezer + Last.fm.

- Nœuds Artist  : image, fans (Deezer), auditeurs/lectures (Last.fm), popularité.
- Nœuds Recording : extrait audio 30s + pochette + rang de popularité (Deezer).
- Relations SIMILAR_TO : artistes similaires (Deezer + Last.fm), reliés UNIQUEMENT
  entre artistes déjà présents dans le graphe (on garde le modèle propre, MBID).

Distinct de COLLABORATED_WITH : SIMILAR_TO = recommandation, pas une vraie collab.
"""
from __future__ import annotations

import logging
from typing import Any

from app.clients.deezer import get_deezer_client
from app.clients.lastfm import get_lastfm_client
from app.config import settings
from app.db.neo4j_driver import run_query, run_write
from app.utils.text import normalize_name

logger = logging.getLogger("sonora.enrich")


def _existing_artist_index() -> dict[str, str]:
    """Table {nom normalisé -> mbid} de tous les artistes déjà en base."""
    rows = run_query("MATCH (a:Artist) RETURN a.mbid AS mbid, a.name AS name")
    return {normalize_name(r["name"]): r["mbid"] for r in rows if r.get("name")}


def _to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _link_similar(a_mbid: str, b_mbid: str, source: str, score: float | None) -> None:
    run_write(
        """
        MATCH (a:Artist {mbid: $a})
        MATCH (b:Artist {mbid: $b})
        MERGE (a)-[s:SIMILAR_TO]-(b)
        SET s.source = $source,
            s.score = coalesce($score, s.score)
        """,
        {"a": a_mbid, "b": b_mbid, "source": source, "score": score},
    )


def _add_genres(mbid: str, tags: list[dict[str, Any]]) -> None:
    for tag in tags[:6]:
        name = (tag.get("name") or "").lower().strip()
        if not name:
            continue
        run_write(
            """
            MATCH (a:Artist {mbid: $mbid})
            MERGE (g:Genre {name: $name})
            MERGE (a)-[:ASSOCIATED_WITH_GENRE]->(g)
            """,
            {"mbid": mbid, "name": name},
        )


def _set_recording_preview(rec_mbid: str, track: dict[str, Any]) -> None:
    """Attache l'ID Deezer + pochette + rang à un Recording.

    On stocke l'ID Deezer (stable), PAS l'URL de preview (token expirant) :
    l'URL fraîche est résolue à la lecture via /api/recordings/:id/preview.
    """
    run_write(
        """
        MATCH (r:Recording {mbid: $mbid})
        SET r.deezer_track_id = $track_id,
            r.cover_url = coalesce($cover, r.cover_url),
            r.deezer_rank = coalesce($rank, r.deezer_rank)
        """,
        {
            "mbid": rec_mbid,
            "track_id": _to_int(track.get("id")),
            "cover": (track.get("album") or {}).get("cover_medium"),
            "rank": _to_int(track.get("rank")),
        },
    )


def enrich_artist(mbid: str, name: str, recording_index: dict[str, dict[str, str]]) -> dict[str, int]:
    """Enrichit un artiste importé. `recording_index` = {titre normalisé -> mbid}."""
    if not settings.enrichment_enabled:
        return {"similar": 0, "previews": 0}

    deezer = get_deezer_client()
    lastfm = get_lastfm_client()

    image_url = deezer_id = None
    fans = listeners = playcount = None
    similar_candidates: list[tuple[str, str, float | None]] = []  # (nom, source, score)
    previews = 0

    # --- Deezer : image, fans, similaires, previews ---
    dz_artist = deezer.search_artist(name)
    if dz_artist:
        image_url = dz_artist.get("picture_big") or dz_artist.get("picture_medium")
        deezer_id = dz_artist.get("id")
        fans = dz_artist.get("nb_fan")

        for rel in deezer.related_artists(deezer_id, limit=settings.similar_max_per_artist):
            if rel.get("name"):
                similar_candidates.append((rel["name"], "deezer", None))

        matched: set[str] = set()

        # 1) Match rapide sur les top tracks Deezer de l'artiste (donne le rang).
        for track in deezer.top_tracks(deezer_id, limit=100):
            rec = recording_index.get(normalize_name(track.get("title")))
            if rec and rec["mbid"] not in matched:
                _set_recording_preview(rec["mbid"], track)
                matched.add(rec["mbid"])
                previews += 1

        # 2) Repli : recherche ciblée (artiste + titre) pour les morceaux restants.
        #    Élargit fortement la couverture des extraits audio.
        for rec in recording_index.values():
            if rec["mbid"] in matched:
                continue
            track = deezer.search_track(name, rec["title"])
            if track:
                _set_recording_preview(rec["mbid"], track)
                matched.add(rec["mbid"])
                previews += 1

    # --- Last.fm : auditeurs, tags, similaires (si clé configurée) ---
    if lastfm.enabled:
        info = lastfm.artist_info(name)
        stats = info.get("stats") or {}
        listeners = _to_int(stats.get("listeners"))
        playcount = _to_int(stats.get("playcount"))
        _add_genres(mbid, (info.get("tags") or {}).get("tag") or [])

        for sim in lastfm.similar_artists(name, limit=settings.similar_max_per_artist):
            if sim.get("name"):
                score = None
                try:
                    score = float(sim.get("match"))
                except (TypeError, ValueError):
                    pass
                similar_candidates.append((sim["name"], "lastfm", score))

    # --- Mise à jour du nœud Artist ---
    run_write(
        """
        MATCH (a:Artist {mbid: $mbid})
        SET a.image_url = coalesce($image_url, a.image_url),
            a.deezer_id = coalesce($deezer_id, a.deezer_id),
            a.fans = coalesce($fans, a.fans),
            a.listeners = coalesce($listeners, a.listeners),
            a.playcount = coalesce($playcount, a.playcount),
            a.popularity = coalesce($fans, $listeners, a.popularity)
        """,
        {
            "mbid": mbid,
            "image_url": image_url,
            "deezer_id": deezer_id,
            "fans": fans,
            "listeners": listeners,
            "playcount": playcount,
        },
    )

    # --- Relations SIMILAR_TO (entre artistes déjà présents) ---
    index = _existing_artist_index()
    self_norm = normalize_name(name)
    linked: set[str] = set()
    similar_count = 0
    for cand_name, source, score in similar_candidates:
        norm = normalize_name(cand_name)
        target_mbid = index.get(norm)
        if not target_mbid or norm == self_norm or target_mbid in linked:
            continue
        _link_similar(mbid, target_mbid, source, score)
        linked.add(target_mbid)
        similar_count += 1

    logger.info(
        "Enrichi « %s » : image=%s, fans=%s, previews=%d, similaires=%d",
        name, bool(image_url), fans, previews, similar_count,
    )
    return {"similar": similar_count, "previews": previews}


def relink_all_similar() -> int:
    """Recalcule les relations SIMILAR_TO entre tous les artistes IMPORTÉS.

    À lancer une fois toute la base peuplée : au moment où un artiste est importé,
    ses similaires ne sont pas encore forcément présents. Cette passe finale
    connecte tout le monde. On ne traite que les artistes ayant des morceaux
    (les vrais imports, pas les collaborateurs créés en passant).
    """
    rows = run_query(
        """
        MATCH (a:Artist)-[:PERFORMED|FEATURED_ON]->(:Recording)
        RETURN DISTINCT a.mbid AS mbid, a.name AS name
        """
    )
    total = 0
    for r in rows:
        total += enrich_artist(r["mbid"], r["name"], {})["similar"]
    logger.info("Re-liaison SIMILAR_TO terminée : %d liens sur %d artistes.", total, len(rows))
    return total
