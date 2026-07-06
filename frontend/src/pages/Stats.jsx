import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api, errMessage } from "../api/client.js";
import { Loader, ErrorState } from "../components/States.jsx";

export default function Stats() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      api.statsOverview(),
      api.topArtists(10),
      api.topCollaborations(10),
      api.topGenres(10),
      api.topRecordings(10),
    ])
      .then(([overview, artists, collabs, genres, recordings]) =>
        setData({ overview, artists, collabs, genres, recordings })
      )
      .catch((e) => setError(errMessage(e)));
  }, []);

  if (error) return <div className="page"><div className="container"><ErrorState message={error} /></div></div>;
  if (!data) return <div className="page"><div className="container"><Loader label="Calcul des statistiques…" /></div></div>;

  const { overview, artists, collabs, genres, recordings } = data;
  const maxGenre = Math.max(...genres.map((g) => g.artists), 1);

  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <h1>Statistiques & analyse</h1>
          <p>Analyse du graphe SONORA : qui est connecté à qui, quelles collaborations dominent, quels genres ressortent.</p>
        </div>

        {/* Overview */}
        <div className="grid grid-stats">
          <Stat value={overview.artists} label="Artistes" />
          <Stat value={overview.recordings} label="Morceaux" />
          <Stat value={overview.releases} label="Albums" />
          <Stat value={overview.collaborations} label="Collaborations" />
          <Stat value={overview.genres} label="Genres" />
        </div>

        <div className="grid" style={{ gridTemplateColumns: "1fr 1fr", marginTop: 32, gap: 24 }}>
          {/* Top artistes */}
          <div>
            <h2 className="section-title"><span className="dot" />Artistes les plus connectés</h2>
            <table className="table">
              <thead><tr><th className="rank">#</th><th>Artiste</th><th>Connexions</th></tr></thead>
              <tbody>
                {artists.map((a, i) => (
                  <tr key={a.mbid} style={{ cursor: "pointer" }} onClick={() => navigate(`/artists/${a.mbid}`)}>
                    <td className="rank">{i + 1}</td>
                    <td>{a.name}</td>
                    <td><span className="badge accent">{a.connections}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Top collaborations */}
          <div>
            <h2 className="section-title"><span className="dot" />Top collaborations</h2>
            <table className="table">
              <thead><tr><th className="rank">#</th><th>Paire d'artistes</th><th>Titres</th></tr></thead>
              <tbody>
                {collabs.map((c, i) => (
                  <tr key={i}>
                    <td className="rank">{i + 1}</td>
                    <td>
                      <Link to={`/artists/${c.source_mbid}`} className="row-title">{c.source}</Link>
                      <span className="dim"> × </span>
                      <Link to={`/artists/${c.target_mbid}`} className="row-title">{c.target}</Link>
                    </td>
                    <td><span className="badge teal">{c.shared_tracks}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="grid" style={{ gridTemplateColumns: "1fr 1fr", marginTop: 32, gap: 24 }}>
          {/* Top genres (barres) */}
          <div>
            <h2 className="section-title"><span className="dot" />Genres les plus présents</h2>
            <div className="card">
              {genres.map((g) => (
                <div key={g.name} style={{ marginBottom: 14 }}>
                  <div className="row between" style={{ marginBottom: 5 }}>
                    <span style={{ fontSize: "0.9rem" }}>{g.name}</span>
                    <span className="dim" style={{ fontSize: "0.82rem" }}>{g.artists}</span>
                  </div>
                  <div style={{ height: 8, background: "var(--surface)", borderRadius: 999 }}>
                    <div style={{ height: "100%", width: `${(g.artists / maxGenre) * 100}%`, background: "var(--gradient)", borderRadius: 999 }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top morceaux */}
          <div>
            <h2 className="section-title"><span className="dot" />Morceaux les plus populaires</h2>
            <table className="table">
              <thead><tr><th className="rank">#</th><th>Titre</th><th>Artistes</th></tr></thead>
              <tbody>
                {recordings.map((r, i) => (
                  <tr key={r.mbid}>
                    <td className="rank">{i + 1}</td>
                    <td><Link to={`/recordings/${r.mbid}`} className="row-title">{r.title}</Link></td>
                    <td className="muted">{r.artist_count > 1 ? `${r.artist_count} artistes` : "solo"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
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
