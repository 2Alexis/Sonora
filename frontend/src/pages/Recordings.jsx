import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, errMessage } from "../api/client.js";
import { Loader, ErrorState, EmptyState } from "../components/States.jsx";
import { PlayButton } from "../components/Player.jsx";
import { formatDuration, year } from "../utils/format.js";

export default function Recordings() {
  const [recordings, setRecordings] = useState(null);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    api.listRecordings({ limit: 200 }).then(setRecordings).catch((e) => setError(errMessage(e)));
  }, []);

  if (error) return <div className="page"><div className="container"><ErrorState message={error} /></div></div>;
  if (!recordings) return <div className="page"><div className="container"><Loader /></div></div>;

  const filtered = filter
    ? recordings.filter((r) => r.title.toLowerCase().includes(filter.toLowerCase()))
    : recordings;

  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <h1>Morceaux</h1>
          <p>{recordings.length} enregistrements dans le graphe, triés par popularité interne.</p>
        </div>

        <input
          className="input"
          style={{ maxWidth: 360, marginBottom: 24 }}
          placeholder="Filtrer par titre…"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />

        {filtered.length === 0 ? (
          <EmptyState title="Aucun morceau" />
        ) : (
          <table className="table">
            <thead>
              <tr><th className="rank">#</th><th></th><th>Titre</th><th>Artistes</th><th>Durée</th><th>1ère sortie</th><th></th></tr>
            </thead>
            <tbody>
              {filtered.map((r, i) => (
                <tr key={r.mbid}>
                  <td className="rank">{i + 1}</td>
                  <td>{r.cover_url ? <img className="cover-thumb" src={r.cover_url} alt="" loading="lazy" /> : null}</td>
                  <td><Link to={`/recordings/${r.mbid}`} className="row-title">{r.title}</Link></td>
                  <td className="muted">{r.artist_count > 1 ? `${r.artist_count} artistes` : "solo"}</td>
                  <td className="muted">{formatDuration(r.length)}</td>
                  <td className="muted">{year(r.first_release_date)}</td>
                  <td><PlayButton track={r} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
