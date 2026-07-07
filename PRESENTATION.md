<div align="center">

# 🎧 SONORA — Support de présentation

### *Explore le graphe du son*

**Exploration des collaborations musicales · MusicBrainz × Deezer × Neo4j**

Projet B3 Dev & B3 Data — *par 2Alexis*

</div>

---

## 📑 Sommaire

1. [Le projet en une phrase](#1-le-projet-en-une-phrase)
2. [Contexte & problématique](#2-contexte--problématique)
3. [Architecture générale](#3-architecture-générale)
4. [Les sources de données](#4-les-sources-de-données)
5. [Le modèle de graphe Neo4j](#5-le-modèle-de-graphe-neo4j)
6. [La détection des collaborations](#6-la-détection-des-collaborations)
7. [La qualité des données](#7-la-qualité-des-données)
8. [L'API backend](#8-lapi-backend)
9. [L'interface web](#9-linterface-web)
10. [L'analyse des données (partie Data)](#10-lanalyse-des-données-partie-data)
11. [Docker & déploiement](#11-docker--déploiement)
12. [Choix techniques justifiés](#12-choix-techniques-justifiés)
13. [Limites connues & pistes d'amélioration](#13-limites-connues--pistes-damélioration)
14. [Questions probables du jury](#14-questions-probables-du-jury)
15. [Déroulé de l'oral (script minuté)](#15-déroulé-de-loral-script-minuté)
16. [Correspondance avec la grille de notation](#16-correspondance-avec-la-grille-de-notation)

---

## 1. Le projet en une phrase

> **SONORA cartographie le réseau invisible des collaborations musicales.**
> Là où Spotify ou Deezer montrent des morceaux, SONORA montre **qui a travaillé
> avec qui** — featurings, collaborations, ponts entre artistes — sous forme d'un
> **graphe explorable**.

**En chiffres (base actuelle) :**

| Artistes | Morceaux | Albums | Collaborations | Genres |
|:---:|:---:|:---:|:---:|:---:|
| **273** | **707** | **592** | **760** | **336** |

---

## 2. Contexte & problématique

Les relations musicales (collaborations, featurings, appartenance à un album,
genre, provenance) forment naturellement un **réseau**. Les modéliser dans une
base **relationnelle** imposerait de multiples tables de jointure et des requêtes
récursives coûteuses pour répondre à « quel chemin relie l'artiste A à
l'artiste B ? ». Une base **graphe** traite ces parcours comme des opérations
natives.

**La problématique du projet :**
> À partir de données MusicBrainz, comment construire un graphe permettant de
> répondre à : quels artistes ont collaboré ? qui apparaît en featuring ? quels
> artistes sont les plus connectés ? quels chemins relient deux artistes ?

SONORA répond à **toutes** ces questions via une API et une interface web.

---

## 3. Architecture générale

```
┌──────────────┐   HTTP/JSON    ┌──────────────────────┐   Bolt    ┌───────────┐
│   Frontend   │ ─────────────▶ │   Backend FastAPI    │ ────────▶ │   Neo4j   │
│ React (Vite) │ ◀───────────── │      (API /api/*)    │ ◀──────── │  (graphe) │
└──────────────┘                └──────────┬───────────┘           └───────────┘
                                           │ HTTPS (rate-limité)
                          ┌────────────────┼─────────────────┐
                          ▼                ▼                 ▼
                   ┌────────────┐   ┌────────────┐   ┌────────────┐
                   │ MusicBrainz│   │   Deezer   │   │  Last.fm   │
                   │ (structure)│   │(enrichisst)│   │(enrichisst)│
                   └────────────┘   └────────────┘   └────────────┘
```

**Backend en couches** (facile à défendre) :
`routers` (HTTP) → `services` (métier) → `clients` (APIs externes) + `db` (Neo4j).
Les routers ne contiennent **aucune** logique métier ; chaque couche est testable
indépendamment.

---

## 4. Les sources de données

SONORA combine **3 APIs**, chacune avec un rôle précis :

| Source | Rôle | Auth | Ce qu'elle apporte |
|--------|------|------|--------------------|
| **MusicBrainz** | 🦴 Colonne vertébrale | User-Agent | Artistes, morceaux, albums, crédits, **MBID** (identifiant anti-doublon) |
| **Deezer** | 🎨 Enrichissement | Aucune | Photos, nb de fans, **extraits audio 30s**, pochettes, artistes similaires |
| **Last.fm** | 📈 Enrichissement | Clé gratuite | Artistes similaires (score), auditeurs, tags/genres |

**Pourquoi cette combinaison et pas Spotify ?**
Spotify a **supprimé fin 2024** les endpoints « artistes similaires » et les
extraits audio 30s pour les nouvelles apps, et ses CGU interdisent de **stocker**
durablement les données — or tout le projet consiste à stocker dans Neo4j.
MusicBrainz (licence ouverte) et l'API publique Deezer sont donc plus adaptés.

---

## 5. Le modèle de graphe Neo4j

### Nœuds

| Label | Clé unique | Propriétés clés |
|-------|-----------|-----------------|
| `Artist` | `mbid` | name, type, country, `image_url`, `fans`, `popularity` |
| `Recording` | `mbid` | title, length, `deezer_track_id`, `cover_url` |
| `Release` | `mbid` | title, date, country, status, release_type |
| `Genre` | `name` | name (normalisé minuscules) |
| `Area` | `mbid`/name | name, type |
| `Label` | `mbid` | name, country |

### Relations

```
(:Artist)-[:PERFORMED]->(:Recording)           (:Artist)-[:COLLABORATED_WITH]-(:Artist)   {shared_tracks}
(:Artist)-[:FEATURED_ON]->(:Recording)         (:Artist)-[:SIMILAR_TO]-(:Artist)          {source, score}
(:Recording)-[:APPEARS_ON]->(:Release)         (:Artist)-[:ASSOCIATED_WITH_GENRE]->(:Genre)
(:Release)-[:RELEASED_IN]->(:Area)             (:Artist)-[:FROM_AREA]->(:Area)
```

**Point clé à mettre en avant : la distinction `COLLABORATED_WITH` vs `SIMILAR_TO`.**
- `COLLABORATED_WITH` = **vraie** collaboration (artistes co-crédités sur un morceau, factuel MusicBrainz).
- `SIMILAR_TO` = **recommandation** (artistes similaires Deezer/Last.fm), gardée séparée pour que l'analyse des collaborations reste honnête.

---

## 6. La détection des collaborations

C'est le cœur algorithmique du projet (`app/utils/collaborations.py`, **testé unitairement**).
Deux signaux combinés :

1. **Structurel** — plusieurs artistes dans le champ `artist-credit` d'un même
   enregistrement ⇒ une relation `COLLABORATED_WITH` pour **chaque paire**
   d'artistes, avec un compteur `shared_tracks` incrémenté à chaque morceau commun.
2. **Textuel** — marqueurs `feat.` / `ft.` / `featuring` / `avec` / `x` / `&` / `vs`.

**Subtilité importante** (à mentionner) : dans une *joinphrase* MusicBrainz,
` & ` signifie un **co-crédit à parts égales** (deux `PERFORMED`), alors que
` feat. ` désigne un **invité** (`FEATURED_ON`). SONORA fait bien la différence.

---

## 7. La qualité des données

| Règle | Implémentation |
|-------|----------------|
| **Anti-doublons** | Contraintes d'unicité sur les `mbid` + `MERGE` systématique |
| **Rate limiting** | 1 req/s vers MusicBrainz (verrou global thread-safe côté client) |
| **Robustesse** | Retries + backoff sur `429`/`503`, exceptions typées, User-Agent identifiable |
| **Données manquantes** | `coalesce()` en écriture : jamais d'écrasement d'une valeur par `null` |
| **Normalisation** | Genres en minuscules ; noms normalisés pour rapprocher les sources |
| **Tests** | Détection des collaborations couverte sans dépendance réseau (`pytest`) |

---

## 8. L'API backend

Tous les endpoints demandés par le cahier des charges sont implémentés,
préfixés par `/api`, documentés automatiquement sur **`/docs`** (Swagger).

- **Recherche & import** : `/search/artists`, `POST /import/artists`
- **Artistes** : `/artists`, `/artists/:id`, `.../recordings`, `.../releases`, `.../collaborations`, `.../similar`
- **Morceaux** : `/recordings`, `/recordings/:id`, `.../artists`, `.../releases`, `.../preview`
- **Albums** : `/releases`, `/releases/:id`, `.../recordings`, `.../artists`
- **Graphe** : `/graph`, `/graph/artists/:id`, `/graph/collaborations`
- **Stats** : `/stats/overview`, `/top-artists`, `/top-collaborations`, `/top-genres`, `/top-recordings`

> 💡 L'endpoint `/recordings/:id/preview` **résout à la volée** une URL Deezer
> fraîche (les URLs d'extraits contiennent un token qui expire) — détail technique
> qui montre la maîtrise.

---

## 9. L'interface web

**7 pages** (React + Vite), avec une **identité graphique** sur le thème son × graphe :

| Page | Contenu |
|------|---------|
| Accueil | Hero + onde sonore animée + stats live |
| Recherche | Grosse barre centrale + **constellation de cartes cliquables** |
| Artistes | Liste (photos Deezer) |
| Fiche artiste | Morceaux (▶ écoute), albums, collaborations, similaires, **ego-graphe** |
| Morceaux | Extraits audio + pochettes |
| Graphe | **Réseau interactif** (collaborations en coral, similarités en violet) |
| Stats | Dashboard analytique |

**Détails d'identité** (pas de template générique) : logo emblème *égaliseur ×
nœuds de graphe*, icônes SVG maison, fond en trame de graphe, marqueurs et loader
en égaliseur animé, **lecteur audio** (extraits Deezer 30s), pochettes de vinyle.

---

## 10. L'analyse des données (partie Data)

Toutes les analyses sont calculées **directement en Cypher** sur le graphe.

**🏆 Artistes les plus connectés** (degré = collaborateurs + morceaux)
| # | Artiste | Connexions |
|---|---------|:---:|
| 1 | JAY-Z | 188 |
| 2 | Beyoncé | 162 |
| 3 | Kendrick Lamar | 142 |
| 4 | Ninho | 133 |
| 5 | SCH | 118 |

**🤝 Top collaborations** (morceaux en commun)
| Paire | Titres |
|-------|:---:|
| Kendrick Lamar × Jay Rock | 17 |
| Dua Lipa × Angèle | 16 |
| J Dilla × JAY-Z | 14 |
| Stromae × ADHDerby | 12 |
| Beyoncé × Slim Thug | 11 |

**🎼 Genres dominants** : hip-hop (132), rap (124), rnb (47), pop (46), french (42)

**Requêtes analytiques avancées** (à montrer en live dans Neo4j Browser) :
```cypher
// Chemin le plus court entre deux artistes
MATCH p = shortestPath(
  (a:Artist {name:"Daft Punk"})-[:COLLABORATED_WITH*..6]-(b:Artist {name:"JAY‐Z"})
) RETURN p;

// Morceaux qui font le pont entre plusieurs artistes
MATCH (a:Artist)-[:PERFORMED|FEATURED_ON]->(r:Recording)<-[:PERFORMED|FEATURED_ON]-(b:Artist)
WHERE a <> b
RETURN r.title, count(DISTINCT a)+count(DISTINCT b) AS artistes
ORDER BY artistes DESC LIMIT 10;
```

---

## 11. Docker & déploiement

**En local** — une seule commande :
```bash
docker compose up -d --build          # Neo4j + backend
docker compose exec backend python -m scripts.seed   # peuple la base
```
→ API sur `:8000/docs`, Neo4j Browser sur `:7474`, front via `npm run dev` (`:5173`).

**En production** — image **tout-en-un** :
- `Dockerfile` racine multi-étapes : **build le frontend** (Vite) puis le **sert
  via l'API** FastAPI (même origine, zéro CORS).
- Hébergé sur **Render** (blueprint `render.yaml`), base **Neo4j Aura Free**.
- Compatible Aura Free (aucune dépendance à APOC).

---

## 12. Choix techniques justifiés

| Décision | Justification |
|----------|---------------|
| **FastAPI** | Validation Pydantic native, docs OpenAPI auto, cohérent avec un profil Data |
| **Neo4j** | Les parcours de graphe (chemins, degrés) sont natifs et performants |
| **`MERGE` par MBID** | Garantit idempotence + zéro doublon |
| **React + Vite** | DX moderne, build rapide, écosystème riche (react-force-graph) |
| **Client MusicBrainz maison** | Contrôle fin du rate limiting (verrou global) et du User-Agent |
| **Deezer sans auth** | Extraits audio + similaires sans OAuth ni contrainte de stockage |
| **Docker Compose** | Environnement reproductible en une commande |

---

## 13. Limites connues & pistes d'amélioration

*(Assumer ses limites = signe de maîtrise, très apprécié à l'oral)*

- **Genres non dédupliqués** : `hip-hop` (MusicBrainz) et `hip hop` (Last.fm tags)
  coexistent → une normalisation/mapping améliorerait les stats de genres.
- **Extraits audio ~65 %** : le matching titre MusicBrainz ↔ Deezer est partiel
  (remixes, versions live, catalogues différents).
- **Areas par pays** : une release est rattachée à une `Area` par code pays, qui
  peut différer de l'`Area` d'origine complète d'un artiste.
- **Profondeur d'import bornée** (`IMPORT_MAX_RECORDINGS`) par politesse envers
  l'API → le graphe est un **échantillon représentatif**, pas un miroir exhaustif.
- **Pistes** : centralité de graphe (PageRank via GDS), détection de communautés,
  peuplement complet des `Label`.

---

## 14. Questions probables du jury

**« Pourquoi un graphe plutôt qu'une base SQL ? »**
Les questions du projet sont des **parcours de réseau** (chemin entre 2 artistes,
degré de connexion). En SQL → jointures récursives coûteuses ; en Neo4j → natif.

**« Comment évitez-vous les doublons ? »**
Contrainte d'unicité sur le `mbid` de chaque nœud + `MERGE` systématique :
réimporter un artiste **met à jour** le nœud existant, sans créer de doublon.

**« Comment détectez-vous une collaboration ? »**
Deux signaux : crédits multiples sur un enregistrement (`artist-credit`) **et**
marqueurs textuels (`feat.`, `&`, `x`…). On distingue `PERFORMED` de `FEATURED_ON`
selon la *joinphrase*.

**« MusicBrainz vs Deezer, quel rôle ? »**
MusicBrainz = **structure factuelle** + MBID (clé anti-doublon, exigée). Deezer =
**enrichissement** (audio, images, similaires). On ne mélange pas les deux rôles.

**« Que se passe-t-il si une API tombe ? »**
Retries + backoff côté MusicBrainz ; l'enrichissement (Deezer/Last.fm) est
**non-bloquant** — s'il échoue, l'import réussit quand même. Neo4j indisponible →
l'API démarre en mode dégradé et `/health` le reflète.

**« Comment garantissez-vous la politesse envers les APIs ? »**
Rate limiter global (verrou thread-safe) : 1 requête/seconde vers MusicBrainz,
throttle léger vers Deezer, User-Agent identifiable.

---

## 15. Déroulé de l'oral (script minuté ~8 min)

| Temps | Étape | À montrer |
|:---:|-------|-----------|
| 0:00 | **Pitch** (1 phrase) | « SONORA cartographie qui a collaboré avec qui » |
| 0:30 | **Problème & choix du graphe** | Slide §2 |
| 1:30 | **Démo — recherche & import** | Page recherche → importer un artiste |
| 3:00 | **Démo — fiche artiste** | Morceaux (▶ écouter un extrait), collaborations, similaires |
| 4:30 | **Démo — le graphe** | Réseau interactif, cliquer un nœud |
| 5:30 | **Démo — stats** | Top artistes/collabs + requête `shortestPath` dans Neo4j Browser |
| 6:30 | **Architecture & modèle** | Schéma §3 + modèle §5 |
| 7:30 | **Qualité + limites** | §7 + §13 (assumer les limites) |
| 8:00 | **Questions** | §14 en tête |

> 💡 Conseil : **lance le seed avant l'oral** (base pleine) et garde **Neo4j
> Browser** ouvert dans un onglet pour la requête `shortestPath` (effet garanti).

---

## 16. Correspondance avec la grille de notation

| Critère | Points | Où c'est traité |
|---------|:---:|-----------------|
| Backend & API | 4 | §8 — API complète FastAPI, tous les endpoints, `/docs` |
| Intégration MusicBrainz | 3 | §4, §6 — client rate-limité, crédits, MBID |
| Modélisation Neo4j | 4 | §5 — nœuds/relations, `SIMILAR_TO` vs `COLLABORATED_WITH` |
| Qualité des données | 3 | §7 — MBID, dedup, rate limit, gestion d'erreurs, tests |
| Interface web | 3 | §9 — 7 pages, graphe interactif, lecteur audio, identité |
| Analyse data | 3 | §10 — top artistes/collabs/genres, requêtes de chemins |
| Docker & organisation | 2 | §11 — Compose + image tout-en-un + archi en couches |
| README & documentation | 3 | `README.md`, `docs/`, ce document |
| Présentation orale | 5 | §15 — script minuté |
| **Total** | **30** | |

---

<div align="center">

**SONORA** — *Explore le graphe du son* 🎧
Repo : https://github.com/2Alexis/Sonora

</div>
