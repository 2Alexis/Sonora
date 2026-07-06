"""Gestion du driver Neo4j (singleton) et helpers d'exécution de requêtes Cypher."""
from __future__ import annotations

import logging
from typing import Any

from neo4j import Driver, GraphDatabase

from app.config import settings

logger = logging.getLogger("sonora.neo4j")

_driver: Driver | None = None


def get_driver() -> Driver:
    """Retourne (ou crée) l'unique instance du driver Neo4j."""
    global _driver
    if _driver is None:
        logger.info("Connexion à Neo4j sur %s", settings.neo4j_uri)
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _driver


def close_driver() -> None:
    """Ferme proprement le driver (appelé au shutdown de l'app)."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


def run_query(cypher: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Exécute une requête Cypher et retourne une liste de dictionnaires."""
    driver = get_driver()
    with driver.session(database=settings.neo4j_database) as session:
        result = session.run(cypher, params or {})
        return [record.data() for record in result]


def run_write(cypher: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Exécute une requête d'écriture dans une transaction managée (retry auto)."""
    driver = get_driver()
    with driver.session(database=settings.neo4j_database) as session:
        return session.execute_write(
            lambda tx: [r.data() for r in tx.run(cypher, params or {})]
        )


def verify_connectivity() -> bool:
    """Vérifie que Neo4j est joignable (utilisé par le healthcheck)."""
    try:
        get_driver().verify_connectivity()
        return True
    except Exception as exc:  # pragma: no cover - dépend de l'infra
        logger.warning("Neo4j injoignable : %s", exc)
        return False
