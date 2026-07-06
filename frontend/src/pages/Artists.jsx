import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, errMessage } from "../api/client.js";
import { Loader, ErrorState, EmptyState } from "../components/States.jsx";
import ArtistCard from "../components/ArtistCard.jsx";

export default function Artists() {
  const [artists, setArtists] = useState(null);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    api.listArtists({ limit: 200 }).then(setArtists).catch((e) => setError(errMessage(e)));
  }, []);

  if (error) return <div className="page"><div className="container"><ErrorState message={error} /></div></div>;
  if (!artists) return <div className="page"><div className="container"><Loader /></div></div>;

  const filtered = filter
    ? artists.filter((a) => a.name.toLowerCase().includes(filter.toLowerCase()))
    : artists;

  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <div className="row between">
            <div>
              <h1>Artistes importés</h1>
              <p>{artists.length} artistes dans le graphe, triés par nombre de morceaux.</p>
            </div>
            <Link to="/search" className="btn btn-primary">+ Importer un artiste</Link>
          </div>
        </div>

        <input
          className="input"
          style={{ maxWidth: 360, marginBottom: 24 }}
          placeholder="Filtrer par nom…"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />

        {filtered.length === 0 ? (
          <EmptyState title="Aucun artiste" hint="Importe des artistes depuis la page Recherche." />
        ) : (
          <div className="grid grid-cards">
            {filtered.map((a) => (
              <ArtistCard key={a.mbid} artist={a} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
