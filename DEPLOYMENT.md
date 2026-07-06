# 🚀 Déployer SONORA en ligne (gratuit, 2 étapes)

SONORA se déploie en **une seule image Docker** (le backend FastAPI sert aussi le
frontend React → même origine, aucun CORS à configurer). Il ne reste que **2 briques** :

| Composant | Service | Rôle |
|---|---|---|
| Base de données | **Neo4j Aura Free** | stocke le graphe des collaborations |
| App (front + API) | **Render** (Docker) | build le front + sert l'API et l'interface |

> Tout est déjà configuré : `Dockerfile` (racine, multi-étapes) + `render.yaml`.
> Le code ne dépend pas d'APOC → compatible Aura Free. **Testé en local via Docker.**

⏱️ ~20-30 min la première fois. Ordre : **1 → 2 → 3**.

---

## 1) Base de données — Neo4j Aura Free

1. Va sur **https://neo4j.com/product/auradb/** → **Start Free** → connecte-toi.
2. **Create instance** → **AuraDB Free**.
3. **Copie/télécharge** les identifiants affichés **une seule fois** :
   - `NEO4J_URI` (format `neo4j+s://xxxx.databases.neo4j.io`)
   - `NEO4J_PASSWORD`
4. Attends l'état **Running** (~2 min).

---

## 2) Remplir la base (seed) — depuis ta machine

Le seed lit `data/seed_artists.json`, interroge MusicBrainz, enrichit via Deezer/Last.fm
et écrit dans Neo4j.

```bash
cd Sonora/backend
pip install -r requirements.txt

# PowerShell (adapte les valeurs Aura) :
$env:NEO4J_URI="neo4j+s://xxxx.databases.neo4j.io"
$env:NEO4J_PASSWORD="ton_mot_de_passe_aura"
$env:MUSICBRAINZ_USER_AGENT="SONORA/1.0 ( ton-email@exemple.com )"

python -m scripts.seed
```

> ⏳ Respecte la limite MusicBrainz (~1 req/s) → laisse finir (quelques minutes).
> Vérifie dans **Aura → Query** : `MATCH (a:Artist) RETURN count(a)` doit renvoyer > 0.

---

## 3) Déployer l'app — Render (Docker)

1. Va sur **https://render.com** → **Sign in with GitHub**.
2. **New +** → **Blueprint** → sélectionne le repo `2Alexis/Sonora`.
   Render lit `render.yaml` et pré-configure le service `sonora`.
3. Renseigne les **variables secrètes** (onglet Environment) :
   - `NEO4J_URI` = l'URI Aura (`neo4j+s://…`)
   - `NEO4J_PASSWORD` = mot de passe Aura
   - `MUSICBRAINZ_USER_AGENT` = `SONORA/1.0 ( ton-email@exemple.com )`
   - `LASTFM_API_KEY` = (optionnel, laisse vide)
4. **Deploy** (le build compile le frontend + installe le backend, ~5-8 min).
5. C'est en ligne : `https://sonora.onrender.com` → recherche un artiste, explore le graphe.

---

## ✅ Résultat

Une seule URL publique (front + API). Teste `https://sonora.onrender.com/health` → `{"status":"ok"}`.

### ⚠️ Limites du gratuit
- **Render Free** : l'app « s'endort » après 15 min d'inactivité → 1er chargement ~50 s (cold start), puis rapide.
- **Aura Free** : l'instance se met en pause après quelques jours d'inactivité → la relancer d'un clic dans la console Aura.
- Parfait comme **démo de portfolio**.

### 🔗 Portfolio
Une fois l'URL Render obtenue, remplace le lien de la carte SONORA par cette URL de démo.

---

<details>
<summary>Alternative : frontend séparé sur Vercel (optionnel)</summary>

Si tu préfères héberger le front à part (CDN Vercel) : déploie `backend/` sur Render
(via l'ancien mode) puis le dossier `frontend/` sur Vercel avec
`VITE_API_URL=https://<backend>/api`, et ajoute l'URL Vercel à `CORS_ORIGINS`.
Le fichier `frontend/vercel.json` est déjà prêt pour ce cas.
</details>
