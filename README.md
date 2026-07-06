<div align="center">

```
   ███████  ██████  ███    ██  ██████  ██████   █████
   ██      ██    ██ ████   ██ ██    ██ ██   ██ ██   ██
   ███████ ██    ██ ██ ██  ██ ██    ██ ██████  ███████
        ██ ██    ██ ██  ██ ██ ██    ██ ██   ██ ██   ██
   ███████  ██████  ██   ████  ██████  ██   ██ ██   ██
```

### 🎧 *Explore le graphe du son*

**Plateforme d'exploration des collaborations musicales — MusicBrainz × Neo4j**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-5.26-008CC1?logo=neo4j&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![MusicBrainz](https://img.shields.io/badge/MusicBrainz-API-BA478F?logo=musicbrainz&logoColor=white)

</div>

---

## 🌌 C'est quoi SONORA ?

**SONORA** est une plateforme façon Spotify/Deezer, mais tournée vers ce que les
plateformes classiques cachent : **le réseau invisible des collaborations entre
artistes**. Qui a travaillé avec qui ? Quel morceau relie deux univers ? Quels
sont les artistes-ponts d'une scène musicale ?

SONORA récupère les données de [MusicBrainz](https://musicbrainz.org), les
**enrichit** via [Deezer](https://developers.deezer.com) et [Last.fm](https://www.last.fm/api)
(images, extraits audio 30s jouables, popularité réelle, artistes similaires),
les modélise sous forme de **graphe** dans Neo4j, et les rend explorables via une
API et une interface web immersive.

> **Palette** : navy spatial `#0B0D17` · coral/amber `#FF6B4A → #FFB347` · teal `#2DD4BF`

---

## 🌐 Démo en ligne

Déploiement gratuit en **2 étapes** : **Neo4j Aura** (base) + **Render** (une image Docker
qui build le front ET sert l'API — même origine, zéro CORS). Guide prêt à l'emploi →
**[DEPLOYMENT.md](DEPLOYMENT.md)** (configs incluses : `Dockerfile` racine + `render.yaml`, testé en local).

## ⚡ Démarrage rapide

```bash
# 1. Cloner et configurer
git clone <repo> sonora && cd sonora
cp .env.example .env          # adapte MUSICBRAINZ_USER_AGENT avec ton email !

# 2. Lancer Neo4j + backend
docker compose up -d --build

# 3. Peupler la base avec le jeu d'artistes de référence
docker compose exec backend python -m scripts.seed

# 4. Explorer
#    API interactive  ->  http://localhost:8000/docs
#    Neo4j Browser    ->  http://localhost:7474  (neo4j / sonora_dev_password)
```

### En local (sans Docker pour le backend)

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
docker compose up -d neo4j          # Neo4j seul via Docker
uvicorn app.main:app --reload
```

---

## 🧩 Architecture

```
Frontend (React/Vite)  ──HTTP──>  Backend FastAPI  ──Bolt──>  Neo4j
                                        │
                                        └──rate-limité──>  API MusicBrainz
```

Détails complets : **[docs/architecture.md](docs/architecture.md)** ·
Modèle de données : **[docs/data-model.md](docs/data-model.md)**

```
sonora/
├── backend/        # API FastAPI (routers → services → db/clients)
├── frontend/       # React + Vite (à venir)
├── data/           # Jeu d'amorçage (seed_artists.json)
├── docs/           # Documentation technique
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🕸️ Modèle de graphe

```
(:Artist)-[:PERFORMED]->(:Recording)          (:Artist)-[:COLLABORATED_WITH]-(:Artist)
(:Artist)-[:FEATURED_ON]->(:Recording)        (:Artist)-[:SIMILAR_TO]-(:Artist)
(:Recording)-[:APPEARS_ON]->(:Release)        (:Artist)-[:ASSOCIATED_WITH_GENRE]->(:Genre)
(:Release)-[:RELEASED_BY]->(:Label)           (:Artist)-[:FROM_AREA]->(:Area)
```

La **détection des collaborations** combine l'analyse des crédits multiples
(`artist-credit`) et la détection textuelle des marqueurs `feat.` / `ft.` /
`avec` / `x` / `&`. Les relations **`SIMILAR_TO`** (Deezer/Last.fm) densifient le
réseau — distinctes des vraies collaborations. → [docs/data-model.md](docs/data-model.md)

---

## 🔌 API

Toutes les routes sont préfixées par `/api`. Documentation interactive : `/docs`.

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET`  | `/api/search/artists?q=` | Recherche d'artistes (MusicBrainz) |
| `POST` | `/api/import/artists` | Importe un artiste `{ mbid }` dans Neo4j |
| `GET`  | `/api/artists` | Liste des artistes importés |
| `GET`  | `/api/artists/:id` | Fiche détaillée d'un artiste |
| `GET`  | `/api/artists/:id/recordings` | Morceaux d'un artiste |
| `GET`  | `/api/artists/:id/releases` | Albums d'un artiste |
| `GET`  | `/api/artists/:id/collaborations` | Collaborateurs d'un artiste |
| `GET`  | `/api/artists/:id/similar` | Artistes similaires (Deezer/Last.fm) |
| `GET`  | `/api/recordings` · `/:id` · `/:id/artists` · `/:id/releases` | Enregistrements |
| `GET`  | `/api/releases` · `/:id` · `/:id/recordings` · `/:id/artists` | Albums |
| `GET`  | `/api/graph` | Graphe global des collaborations |
| `GET`  | `/api/graph/artists/:id` | Ego-network d'un artiste |
| `GET`  | `/api/graph/collaborations` | Graphe des collaborations |
| `GET`  | `/api/stats/overview` | Statistiques globales |
| `GET`  | `/api/stats/top-artists` | Artistes les plus connectés |
| `GET`  | `/api/stats/top-collaborations` | Top collaborations |
| `GET`  | `/api/stats/top-genres` | Top genres |
| `GET`  | `/api/stats/top-recordings` | Top morceaux |

### Exemple de flux complet

```bash
# Chercher Daft Punk
curl "http://localhost:8000/api/search/artists?q=Daft%20Punk"

# Importer (avec le mbid retourné)
curl -X POST http://localhost:8000/api/import/artists \
     -H "Content-Type: application/json" \
     -d '{"mbid": "056e4f3e-d505-4dad-8ec1-d04f521cbb56"}'

# Voir les artistes les plus connectés
curl http://localhost:8000/api/stats/top-artists
```

---

## 📊 Partie Data

SONORA répond aux questions analytiques du projet via `/api/stats/*` :
top artistes les plus connectés, top collaborations, top morceaux, top genres,
statistiques globales — le tout calculé directement en **Cypher** sur le graphe.
Voir aussi les requêtes d'exemple (chemin le plus court entre deux artistes,
morceaux-ponts) dans [docs/data-model.md](docs/data-model.md).

---

## ✅ Qualité des données

- **Anti-doublons** : contraintes d'unicité sur les MBID + `MERGE` systématique.
- **Rate limiting** : 1 requête/s vers MusicBrainz (verrou global côté client).
- **Robustesse** : retries + backoff sur 429/503, User-Agent identifiable.
- **Données manquantes** : `coalesce()` en écriture, jamais d'écrasement par `null`.
- **Tests** : `cd backend && pytest` (détection de collaborations couverte).

---

## 🗺️ Roadmap

- [x] Backend FastAPI complet (API + intégration MusicBrainz)
- [x] Modélisation Neo4j + détection des collaborations
- [x] Enrichissement Deezer + Last.fm (images, previews, popularité, `SIMILAR_TO`)
- [x] Statistiques / analyse data
- [x] Docker Compose + seed
- [x] **Frontend React/Vite** (accueil, recherche, artistes, graphe interactif, stats, lecteur audio)
- [ ] Peuplement des `Label` / `RELEASED_BY`

---

## 📚 Crédits & conformité

Données fournies par **[MusicBrainz](https://musicbrainz.org)** sous licence
[CC](https://musicbrainz.org/doc/About/Data_License). SONORA respecte les
[règles d'usage de l'API](https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting)
(User-Agent identifiable, 1 requête/seconde).

<div align="center">

**SONORA** — *Explore le graphe du son* 🎧

</div>
