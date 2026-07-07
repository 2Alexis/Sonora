import { useEffect, useState } from "react";
import { api, errMessage } from "../api/client.js";
import { Loader, ErrorState, EmptyState } from "../components/States.jsx";
import GraphView from "../components/GraphView.jsx";

const DENSITIES = [
  { value: 100, label: "100" },
  { value: 300, label: "300" },
  { value: 5000, label: "Tout" },
];

export default function Graph() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [limit, setLimit] = useState(300);

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
              <p>
                Le réseau des artistes reliés par leurs collaborations et similarités.
                Glisse, zoome, clique sur un nœud.
                {data && (
                  <> {" "}
                    <span className="muted">
                      — <strong>{data.nodes.length}</strong> artistes ·{" "}
                      <strong>{data.edges.length}</strong> liens affichés
                    </span>
                  </>
                )}
              </p>
            </div>
            <div className="row">
              <span className="dim" style={{ fontSize: "0.85rem" }}>Densité :</span>
              {DENSITIES.map((d) => (
                <button
                  key={d.value}
                  className={"btn btn-sm" + (limit === d.value ? " btn-primary" : "")}
                  onClick={() => setLimit(d.value)}
                >
                  {d.label}
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
