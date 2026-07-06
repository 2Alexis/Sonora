# 🏛️ Architecture technique de SONORA

## Vue d'ensemble

```
┌──────────────┐     HTTP/JSON      ┌──────────────────────┐     Bolt      ┌───────────┐
│   Frontend   │  ───────────────>  │   Backend FastAPI    │  ──────────>  │   Neo4j   │
│ React (Vite) │  <───────────────  │  (API /api/*)        │  <──────────  │  (graphe) │
└──────────────┘                    └──────────┬───────────┘               └───────────┘
                                               │ HTTPS (rate-limité 1 req/s)
                                               ▼
                                      ┌──────────────────┐
                                      │   MusicBrainz    │
                                      │   (API externe)  │
                                      └──────────────────┘
```

## Couches du backend

Le backend suit une architecture en couches claire (facile à défendre à l'oral) :

```
app/
├── main.py            # Assemblage FastAPI, CORS, lifespan (schéma au démarrage)
├── config.py          # Configuration typée (pydantic-settings) depuis l'env
├── clients/
│   └── musicbrainz.py # Accès à l'API externe : rate limiting, retries, erreurs
├── db/
│   ├── neo4j_driver.py# Driver singleton + helpers run_query / run_write
│   └── constraints.py # Contraintes d'unicité + index (anti-doublons)
├── models/
│   └── schemas.py     # Contrats Pydantic (validation entrée/sortie)
├── services/          # LOGIQUE MÉTIER (aucun détail HTTP ici)
│   ├── import_service.py    # MusicBrainz -> normalisation -> Neo4j
│   ├── search_service.py
│   ├── artist_service.py
│   ├── recording_service.py
│   ├── release_service.py
│   ├── graph_service.py     # Construction nodes/edges pour la viz
│   └── stats_service.py     # Analyses (top artistes, collabs, genres)
├── routers/           # ENDPOINTS HTTP (fine couche, délègue aux services)
└── utils/
    └── collaborations.py    # Détection feat/collab (testée unitairement)
```

**Principe** : les *routers* ne contiennent aucune logique métier ; ils valident
l'entrée et appellent un *service*. Les *services* orchestrent le client externe
et la base. Ce découpage rend chaque partie testable indépendamment.

## Flux d'import (le plus important)

1. `POST /api/import/artists { mbid }`
2. `import_service` appelle `musicbrainz.get_artist()` → `MERGE (:Artist)`
3. Rattachement `FROM_AREA` + `ASSOCIATED_WITH_GENRE`
4. `musicbrainz.browse_recordings()` → pour chaque morceau :
   - `MERGE (:Recording)` + relations `PERFORMED` / `FEATURED_ON`
   - détection des paires `COLLABORATED_WITH`
   - `MERGE (:Release)` + `APPEARS_ON` + `RELEASED_IN`
5. Retour d'un `ImportSummary` (compteurs).

## Choix techniques

| Décision | Justification |
|----------|---------------|
| **FastAPI** | Validation Pydantic native, docs OpenAPI auto (`/docs`), async-ready |
| **Driver Neo4j officiel** | Transactions managées, `MERGE` idempotent |
| **Client MusicBrainz maison** | Contrôle fin du rate limiting (verrou global) et du User-Agent |
| **`MERGE` partout** | Garantit l'idempotence et l'absence de doublons via MBID |
| **Singletons (driver, client)** | Un seul pool de connexions, un seul rate-limiter global |
| **Docker Compose** | Neo4j + backend reproductibles en une commande |

## Gestion des erreurs

- Erreurs MusicBrainz → `MusicBrainzError` → HTTP `502 Bad Gateway` côté API.
- Ressource absente en base → HTTP `404`.
- Neo4j indisponible au démarrage → l'API démarre quand même (mode dégradé),
  le schéma est appliqué dès que possible ; `/health` reflète l'état réel.

## Tests

- `tests/test_collaborations.py` : couvre la détection feat/collab **sans réseau**
  (logique pure), le point le plus sensible du projet.
- Lancement : `pytest` depuis `backend/`.
