import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";

const FEATURES = [
  { icon: "🔎", title: "Recherche MusicBrainz", text: "Trouve n'importe quel artiste et importe-le dans le graphe en un clic." },
  { icon: "🕸️", title: "Graphe de collaborations", text: "Visualise qui a travaillé avec qui, les featurings et les ponts entre univers." },
  { icon: "📊", title: "Analyse data", text: "Artistes les plus connectés, top collaborations, genres dominants — en direct." },
];

export default function Home() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.statsOverview().then(setStats).catch(() => setStats(null));
  }, []);

  return (
    <div className="page">
      <div className="container">
        {/* Hero */}
        <section style={{ padding: "40px 0 20px", textAlign: "center" }}>
          <span className="badge accent">🎧 MusicBrainz × Neo4j</span>
          <h1 style={{ fontSize: "3.4rem", margin: "20px 0 10px", lineHeight: 1.05 }}>
            Explore le <span className="gradient-text">graphe du son</span>
          </h1>
          <p className="muted" style={{ maxWidth: 620, margin: "0 auto 28px", fontSize: "1.1rem" }}>
            SONORA cartographie le réseau invisible des collaborations musicales :
            artistes, morceaux, albums, featurings. Ce que les plateformes cachent,
            on le rend visible.
          </p>
          <div className="row" style={{ justifyContent: "center" }}>
            <Link to="/search" className="btn btn-primary">🔎 Rechercher un artiste</Link>
            <Link to="/graph" className="btn">Voir le graphe</Link>
          </div>
        </section>

        {/* Stats live */}
        {stats && (
          <section className="grid grid-stats mt-lg">
            <Stat value={stats.artists} label="Artistes" />
            <Stat value={stats.recordings} label="Morceaux" />
            <Stat value={stats.releases} label="Albums" />
            <Stat value={stats.collaborations} label="Collaborations" />
            <Stat value={stats.genres} label="Genres" />
          </section>
        )}

        {/* Features */}
        <section className="grid grid-cards mt-lg" style={{ marginTop: 48 }}>
          {FEATURES.map((f) => (
            <div className="card" key={f.title}>
              <div style={{ fontSize: "2rem", marginBottom: 12 }}>{f.icon}</div>
              <h3 style={{ marginBottom: 8 }}>{f.title}</h3>
              <p className="muted" style={{ fontSize: "0.92rem" }}>{f.text}</p>
            </div>
          ))}
        </section>
      </div>
    </div>
  );
}

function Stat({ value, label }) {
  return (
    <div className="stat-card">
      <div className="stat-value gradient-text">{value ?? "—"}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}
