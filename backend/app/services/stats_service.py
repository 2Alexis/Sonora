"""Analyses / statistiques du graphe (partie Data du projet).

Répond aux questions du cahier des charges :
- artistes les plus connectés,
- top collaborations,
- genres les plus présents,
- statistiques globales.
"""
from __future__ import annotations

from typing import Any

from app.db.neo4j_driver import run_query


def overview() -> dict[str, int]:
    cypher = """
    OPTIONAL MATCH (a:Artist)   WITH count(DISTINCT a) AS artists
    OPTIONAL MATCH (r:Recording) WITH artists, count(DISTINCT r) AS recordings
    OPTIONAL MATCH (rel:Release) WITH artists, recordings, count(DISTINCT rel) AS releases
    OPTIONAL MATCH (g:Genre)     WITH artists, recordings, releases, count(DISTINCT g) AS genres
    OPTIONAL MATCH (:Artist)-[c:COLLABORATED_WITH]-(:Artist)
    RETURN artists, recordings, releases, genres,
           count(c) / 2 AS collaborations
    """
    rows = run_query(cypher)
    return rows[0] if rows else {
        "artists": 0, "recordings": 0, "releases": 0, "genres": 0, "collaborations": 0
    }


def top_artists(limit: int = 10) -> list[dict[str, Any]]:
    """Artistes les plus connectés = degré le plus élevé (collabs + morceaux)."""
    cypher = """
    MATCH (a:Artist)
    OPTIONAL MATCH (a)-[:COLLABORATED_WITH]-(other:Artist)
    OPTIONAL MATCH (a)-[:PERFORMED|FEATURED_ON]->(rec:Recording)
    WITH a, count(DISTINCT other) AS collabs, count(DISTINCT rec) AS tracks
    RETURN a.mbid AS mbid, a.name AS name, (collabs + tracks) AS connections
    ORDER BY connections DESC, a.name ASC
    LIMIT $limit
    """
    return run_query(cypher, {"limit": limit})


def top_collaborations(limit: int = 10) -> list[dict[str, Any]]:
    cypher = """
    MATCH (a:Artist)-[r:COLLABORATED_WITH]-(b:Artist)
    WHERE a.mbid < b.mbid
    RETURN a.name AS source, a.mbid AS source_mbid,
           b.name AS target, b.mbid AS target_mbid,
           coalesce(r.shared_tracks, 1) AS shared_tracks
    ORDER BY shared_tracks DESC, source ASC
    LIMIT $limit
    """
    return run_query(cypher, {"limit": limit})


def top_genres(limit: int = 10) -> list[dict[str, Any]]:
    cypher = """
    MATCH (g:Genre)<-[:ASSOCIATED_WITH_GENRE]-(a:Artist)
    RETURN g.name AS name, count(DISTINCT a) AS artists
    ORDER BY artists DESC, name ASC
    LIMIT $limit
    """
    return run_query(cypher, {"limit": limit})


def top_recordings(limit: int = 10) -> list[dict[str, Any]]:
    cypher = """
    MATCH (rec:Recording)
    OPTIONAL MATCH (a:Artist)-[:PERFORMED|FEATURED_ON]->(rec)
    WITH rec, count(DISTINCT a) AS artist_count
    RETURN rec.mbid AS mbid, rec.title AS title,
           coalesce(rec.popularity, 0) AS popularity, artist_count
    ORDER BY popularity DESC, artist_count DESC
    LIMIT $limit
    """
    return run_query(cypher, {"limit": limit})
