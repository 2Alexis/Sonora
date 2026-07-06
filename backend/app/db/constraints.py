"""Contraintes d'unicité et index Neo4j.

L'unicité sur le MBID est la garantie anti-doublons exigée par le cahier des charges :
chaque MERGE sur un mbid ne peut créer qu'un seul nœud.
"""
from __future__ import annotations

import logging

from app.db.neo4j_driver import run_write

logger = logging.getLogger("sonora.neo4j")

CONSTRAINTS = [
    "CREATE CONSTRAINT artist_mbid IF NOT EXISTS FOR (a:Artist) REQUIRE a.mbid IS UNIQUE",
    "CREATE CONSTRAINT recording_mbid IF NOT EXISTS FOR (r:Recording) REQUIRE r.mbid IS UNIQUE",
    "CREATE CONSTRAINT release_mbid IF NOT EXISTS FOR (r:Release) REQUIRE r.mbid IS UNIQUE",
    "CREATE CONSTRAINT label_mbid IF NOT EXISTS FOR (l:Label) REQUIRE l.mbid IS UNIQUE",
    "CREATE CONSTRAINT area_mbid IF NOT EXISTS FOR (a:Area) REQUIRE a.mbid IS UNIQUE",
    "CREATE CONSTRAINT genre_name IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE",
]

INDEXES = [
    "CREATE INDEX artist_name IF NOT EXISTS FOR (a:Artist) ON (a.name)",
    "CREATE INDEX recording_title IF NOT EXISTS FOR (r:Recording) ON (r.title)",
    "CREATE INDEX release_title IF NOT EXISTS FOR (r:Release) ON (r.title)",
]


def apply_schema() -> None:
    """Applique contraintes + index (idempotent grâce à IF NOT EXISTS)."""
    for stmt in CONSTRAINTS + INDEXES:
        run_write(stmt)
    logger.info("Schéma Neo4j appliqué (%d contraintes, %d index).", len(CONSTRAINTS), len(INDEXES))
