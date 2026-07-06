import { useEffect, useState } from "react";
import { api, errMessage } from "../api/client.js";
import { Loader, ErrorState, EmptyState } from "../components/States.jsx";
import GraphView from "../components/GraphView.jsx";

export default function Graph() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [limit, setLimit] = useState(150);

  useEffect(() => {
    setData(null);
    api.getGraph(limit).then(setData).catch((e) => setError(errMessage(e)));
  }, [limit]);

  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <div className="row between">
            <div>
              <h1>Graphe des collaborations</h1>
              <p>Le réseau des artistes reliés par leurs collaborations. Glisse, zoome, clique sur un nœud.</p>
            </div>
            <div className="row">
              <span className="dim" style={{ fontSize: "0.85rem" }}>Densité :</span>
              {[80, 150, 300].map((n) => (
                <button
                  key={n}
                  className={"btn btn-sm" + (limit === n ? " btn-primary" : "")}
                  onClick={() => setLimit(n)}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>
        </div>

        {error && <ErrorState message={error} />}
        {!error && !data && <Loader label="Construction du graphe…" />}
        {!error && data && (data.nodes.length === 0
          ? <EmptyState title="Graphe vide" hint="Importe des artistes pour peupler le réseau." />
          : <GraphView data={data} height={620} />
        )}
      </div>
    </div>
  );
}
