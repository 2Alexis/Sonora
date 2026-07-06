"""Service d'import : orchestre MusicBrainz -> normalisation -> Neo4j.

Toute la logique anti-doublons repose sur MERGE par MBID (cf. constraints.py).
La détection de collaborations est déléguée à app.utils.collaborations.
"""
from __future__ import annotations

import logging
from typing import Any

from app.clients.musicbrainz import MusicBrainzError, get_musicbrainz_client
from app.config import settings
from app.db.neo4j_driver import run_write
from app.models.schemas import Artist, ImportSummary
from app.services import enrichment_service
from app.utils.collaborations import (
    collaboration_pairs,
    parse_artist_credit,
    split_performers_and_features,
    title_suggests_collaboration,
)
from app.utils.text import normalize_name

logger = logging.getLogger("sonora.import")


# --------------------------------------------------------------------------- #
# Normalisation MusicBrainz -> propriétés de nœuds
# --------------------------------------------------------------------------- #
def normalize_artist(raw: dict[str, Any]) -> dict[str, Any]:
    life = raw.get("life-span", {}) or {}
    return {
        "mbid": raw.get("id"),
        "name": raw.get("name") or "Unknown",
        "type": raw.get("type"),
        "country": raw.get("country"),
        "gender": raw.get("gender"),
        "begin_date": life.get("begin"),
        "end_date": life.get("end"),
        "disambiguation": raw.get("disambiguation"),
    }


def normalize_recording(raw: dict[str, Any]) -> dict[str, Any]:
    releases = raw.get("releases", []) or []
    # Score de popularité INTERNE : proxy simple = nb de releases où le morceau
    # apparaît (plus un titre est réédité/compilé, plus il est "populaire").
    popularity = float(len(releases))
    return {
        "mbid": raw.get("id"),
        "title": raw.get("title") or "Untitled",
        "length": raw.get("length"),
        "first_release_date": raw.get("first-release-date"),
        "popularity": popularity,
        "source": "musicbrainz",
    }


def normalize_release(raw: dict[str, Any]) -> dict[str, Any]:
    rg = raw.get("release-group", {}) or {}
    return {
        "mbid": raw.get("id"),
        "title": raw.get("title") or "Untitled",
        "date": raw.get("date"),
        "country": raw.get("country"),
        "status": raw.get("status"),
        "release_type": rg.get("primary-type") or raw.get("packaging"),
    }


# --------------------------------------------------------------------------- #
# Écriture Neo4j
# --------------------------------------------------------------------------- #
def _upsert_artist(props: dict[str, Any]) -> None:
    """Crée/actualise un Artist. Ne pas écraser un nom existant par vide."""
    run_write(
        """
        MERGE (a:Artist {mbid: $mbid})
        SET a.name = coalesce($name, a.name),
            a.type = coalesce($type, a.type),
            a.country = coalesce($country, a.country),
            a.gender = coalesce($gender, a.gender),
            a.begin_date = coalesce($begin_date, a.begin_date),
            a.end_date = coalesce($end_date, a.end_date),
            a.disambiguation = coalesce($disambiguation, a.disambiguation)
        """,
        props,
    )


def _link_artist_area(artist_mbid: str, area: dict[str, Any] | None) -> None:
    if not area or not area.get("id"):
        return
    run_write(
        """
        MATCH (a:Artist {mbid: $artist_mbid})
        MERGE (ar:Area {mbid: $area_mbid})
        SET ar.name = $name, ar.type = $type
        MERGE (a)-[:FROM_AREA]->(ar)
        """,
        {
            "artist_mbid": artist_mbid,
            "area_mbid": area["id"],
            "name": area.get("name"),
            "type": area.get("type"),
        },
    )


def _link_artist_genres(artist_mbid: str, genres: list[dict[str, Any]] | None) -> None:
    for genre in genres or []:
        name = genre.get("name")
        if not name:
            continue
        run_write(
            """
            MATCH (a:Artist {mbid: $artist_mbid})
            MERGE (g:Genre {name: $name})
            MERGE (a)-[r:ASSOCIATED_WITH_GENRE]->(g)
            SET r.count = $count
            """,
            {"artist_mbid": artist_mbid, "name": name.lower(), "count": genre.get("count")},
        )


def _upsert_recording_with_credits(rec_props: dict[str, Any], credits: list[dict[str, Any]]) -> None:
    """Crée le Recording, ses artistes crédités et les relations PERFORMED/FEATURED_ON."""
    run_write(
        """
        MERGE (r:Recording {mbid: $mbid})
        SET r.title = $title,
            r.length = $length,
            r.first_release_date = $first_release_date,
            r.popularity = $popularity,
            r.source = $source
        """,
        rec_props,
    )

    performers, features = split_performers_and_features(credits)

    for perf in performers:
        _upsert_artist({**_blank_artist(), "mbid": perf["mbid"], "name": perf["name"]})
        run_write(
            """
            MATCH (a:Artist {mbid: $artist_mbid})
            MATCH (r:Recording {mbid: $rec_mbid})
            MERGE (a)-[:PERFORMED]->(r)
            """,
            {"artist_mbid": perf["mbid"], "rec_mbid": rec_props["mbid"]},
        )

    for feat in features:
        _upsert_artist({**_blank_artist(), "mbid": feat["mbid"], "name": feat["name"]})
        run_write(
            """
            MATCH (a:Artist {mbid: $artist_mbid})
            MATCH (r:Recording {mbid: $rec_mbid})
            MERGE (a)-[:FEATURED_ON]->(r)
            """,
            {"artist_mbid": feat["mbid"], "rec_mbid": rec_props["mbid"]},
        )


def _link_collaborations(credits: list[dict[str, Any]]) -> int:
    """Crée les relations COLLABORATED_WITH (avec compteur de morceaux partagés)."""
    pairs = collaboration_pairs(credits)
    for a, b in pairs:
        run_write(
            """
            MATCH (x:Artist {mbid: $a})
            MATCH (y:Artist {mbid: $b})
            MERGE (x)-[r:COLLABORATED_WITH]-(y)
            SET r.shared_tracks = coalesce(r.shared_tracks, 0) + 1
            """,
            {"a": a, "b": b},
        )
    return len(pairs)


def _upsert_releases_for_recording(rec_mbid: str, releases: list[dict[str, Any]]) -> int:
    """Crée les Release, la relation APPEARS_ON et RELEASED_IN (par pays)."""
    count = 0
    for raw_rel in releases[: settings.import_max_releases_per_recording]:
        rel = normalize_release(raw_rel)
        if not rel["mbid"]:
            continue
        run_write(
            """
            MATCH (rec:Recording {mbid: $rec_mbid})
            MERGE (rel:Release {mbid: $mbid})
            SET rel.title = $title,
                rel.date = $date,
                rel.country = $country,
                rel.status = $status,
                rel.release_type = $release_type
            MERGE (rec)-[:APPEARS_ON]->(rel)
            """,
            {**rel, "rec_mbid": rec_mbid},
        )
        # RELEASED_IN : rattachement au pays de sortie (Area par nom).
        if rel["country"]:
            run_write(
                """
                MATCH (rel:Release {mbid: $mbid})
                MERGE (ar:Area {name: $country})
                ON CREATE SET ar.type = 'Country'
                MERGE (rel)-[:RELEASED_IN]->(ar)
                """,
                {"mbid": rel["mbid"], "country": rel["country"]},
            )
        count += 1
    return count


def _blank_artist() -> dict[str, Any]:
    """Gabarit d'artiste vide (pour les MERGE de co-crédités partiels)."""
    return {
        "mbid": None,
        "name": None,
        "type": None,
        "country": None,
        "gender": None,
        "begin_date": None,
        "end_date": None,
        "disambiguation": None,
    }


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def import_artist(mbid: str, include_recordings: bool = True, max_recordings: int | None = None) -> ImportSummary:
    """Importe un artiste complet dans Neo4j depuis son MBID MusicBrainz."""
    client = get_musicbrainz_client()

    raw_artist = client.get_artist(mbid)
    artist_props = normalize_artist(raw_artist)
    if not artist_props["mbid"]:
        raise MusicBrainzError(f"Artiste introuvable pour le MBID {mbid}")

    _upsert_artist(artist_props)
    _link_artist_area(artist_props["mbid"], raw_artist.get("area"))
    _link_artist_genres(artist_props["mbid"], raw_artist.get("genres"))

    recordings_imported = 0
    releases_imported = 0
    collaborators_detected = 0
    features_detected = 0
    # Index {titre normalisé -> mbid} pour rattacher les previews Deezer ensuite.
    recording_index: dict[str, str] = {}

    if include_recordings:
        limit = max_recordings or settings.import_max_recordings
        recordings = client.browse_recordings(mbid, limit=limit)
        for raw_rec in recordings:
            rec_props = normalize_recording(raw_rec)
            if not rec_props["mbid"]:
                continue
            recording_index[normalize_name(rec_props["title"])] = {
                "mbid": rec_props["mbid"],
                "title": rec_props["title"],
            }

            credits = parse_artist_credit(raw_rec.get("artist-credit"))
            # Filet de sécurité : si MusicBrainz ne renvoie aucun crédit, on relie
            # au moins l'artiste importé (le morceau a été browsé via son MBID).
            if not credits:
                credits = [
                    {
                        "mbid": artist_props["mbid"],
                        "name": artist_props["name"],
                        "joinphrase": "",
                        "is_featured": False,
                    }
                ]
            # Filet de sécurité : si le titre suggère un feat mais que les crédits
            # ne le reflètent pas, on garde au moins le morceau comme collaboratif.
            rec_props["is_collaboration"] = (
                len(credits) > 1 or title_suggests_collaboration(rec_props["title"])
            )

            _upsert_recording_with_credits(rec_props, credits)
            releases_imported += _upsert_releases_for_recording(
                rec_props["mbid"], raw_rec.get("releases", []) or []
            )

            if len(credits) > 1:
                collaborators_detected += _link_collaborations(credits)
                features_detected += sum(1 for c in credits if c["is_featured"])

            recordings_imported += 1

    # --- Enrichissement Deezer + Last.fm (image, fans, previews, SIMILAR_TO) ---
    similar_detected = 0
    previews_added = 0
    if settings.enrichment_enabled:
        try:
            stats = enrichment_service.enrich_artist(
                artist_props["mbid"], artist_props["name"], recording_index
            )
            similar_detected = stats["similar"]
            previews_added = stats["previews"]
        except Exception as exc:  # l'enrichissement ne doit jamais casser l'import
            logger.warning("Enrichissement ignoré pour %s : %s", artist_props["name"], exc)

    return ImportSummary(
        artist=Artist(**artist_props),
        recordings_imported=recordings_imported,
        releases_imported=releases_imported,
        collaborators_detected=collaborators_detected,
        features_detected=features_detected,
        similar_detected=similar_detected,
        previews_added=previews_added,
        message=f"Artiste « {artist_props['name']} » importé avec succès.",
    )
