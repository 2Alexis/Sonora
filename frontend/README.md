# 🎨 Frontend SONORA (React + Vite)

Interface d'exploration du graphe du son : recherche, import, fiches artistes,
graphe interactif, statistiques, et **lecteur audio** (extraits 30s Deezer).

## Stack

- **React 18 + Vite 6**
- **React Router** — 7 pages
- **react-force-graph-2d** — visualisation canvas du graphe
- **axios** — appels API (proxy Vite `/api` → backend `:8000`)

## Démarrage

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

Le backend doit tourner sur `:8000` (via `docker compose up -d`). Vite proxifie
automatiquement `/api` vers le backend (voir `vite.config.js`), donc aucun souci
de CORS en dev.

Pour builder en production : `npm run build` (sortie dans `dist/`).

## Pages

| Route | Contenu |
|-------|---------|
| `/` | Accueil + stats live |
| `/search` | Recherche MusicBrainz + import en un clic |
| `/artists` | Liste des artistes (photos Deezer) |
| `/artists/:id` | Fiche : morceaux (play), albums, collaborations, similaires, ego-graphe |
| `/recordings` | Morceaux avec extraits audio + pochettes |
| `/graph` | Graphe interactif (collaborations en coral, similarités en violet) |
| `/stats` | Dashboard analytique |

## Thème

- Fond : navy spatial `#0B0D17`
- Accent : dégradé coral → amber `#FF6B4A → #FFB347`
- Secondaire : teal `#2DD4BF` · similarités `#A78BFA`
- Typo : Space Grotesk (titres) + Inter (texte)
