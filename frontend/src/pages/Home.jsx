import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";
import { Mark } from "../components/Logo.jsx";
import { IconSearch, IconGraph, IconNodes, IconStats } from "../components/Icons.jsx";

const FEATURES = [
  { Icon: IconSearch, title: "Recherche MusicBrainz", text: "Trouve n'importe quel artiste et importe-le dans le graphe en un clic." },
  { Icon: IconGraph, title: "Graphe de collaborations", text: "Visualise qui a travaillé avec qui, les featurings et les ponts entre univers." },
  { Icon: IconStats, title: "Analyse data", text: "Artistes les plus connectés, top collaborations, genres dominants — en direct." },
];

// Onde sonore décorative (signal en pointillés qui s'écoule).
function HeroWave() {
  const wave = (y, amp) => {
    let d = `M-60 ${y}`;
    for (let x = -60; x <= 1260; x += 60) d += ` Q ${x + 30} ${y - amp} ${x + 60} ${y} T ${x + 120} ${y}`;
    return d;
  };
  return (
    <svg className="hero-wave" viewBox="0 0 1200 260" fill="none" aria-hidden="true">
      <defs>
        <linearGradient id="hw1" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#FF6B4A" stopOpacity="0" />
          <stop offset="0.5" stopColor="#FFB347" />
          <stop offset="1" stopColor="#FF6B4A" stopOpacity="0" />
        </linearGradient>
        <linearGradient id="hw2" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#2DD4BF" stopOpacity="0" />
          <stop offset="0.5" stopColor="#2DD4BF" />
          <stop offset="1" stopColor="#2DD4BF" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={wave(130, 46)} stroke="url(#hw1)" strokeWidth="2" strokeDasharray="2 12" strokeLinecap="round" />
      <path d={wave(140, 30)} stroke="url(#hw2)" strokeWidth="2" strokeDasharray="2 14" strokeLinecap="round" style={{ animationDelay: "-3s" }} />
    </svg>
  );
}

export default function Home() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.statsOverview().then(setStats).catch(() => setStats(null));
  }, []);

  return (
    <div className="page">
      <div className="container">
        {/* Hero */}
        <section className="hero" style={{ padding: "56px 0 24px", textAlign: "center" }}>
          <HeroWave />
          <span className="badge accent">
            <Mark size={15} /> MusicBrainz · Deezer · Neo4j
          </span>
          <h1 style={{ fontSize: "3.5rem", margin: "22px 0 12px", lineHeight: 1.04 }}>
            Explore le <span className="gradient-text">graphe du son</span>
          </h1>
          <p className="muted" style={{ maxWidth: 620, margin: "0 auto 30px", fontSize: "1.1rem" }}>
            SONORA cartographie le réseau invisible des collaborations musicales :
            artistes, morceaux, albums, featurings. Ce que les plateformes cachent,
            on le rend visible.
          </p>
          <div className="row" style={{ justifyContent: "center" }}>
            <Link to="/search" className="btn btn-primary"><IconSearch width={17} height={17} /> Rechercher un artiste</Link>
            <Link to="/graph" className="btn"><IconGraph width={17} height={17} /> Voir le graphe</Link>
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
          {FEATURES.map(({ Icon, title, text }) => (
            <div className="card" key={title}>
              <div className="feature-icon"><Icon width={22} height={22} /></div>
              <h3 style={{ marginBottom: 8 }}>{title}</h3>
              <p className="muted" style={{ fontSize: "0.92rem" }}>{text}</p>
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
