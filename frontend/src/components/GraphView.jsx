import { useEffect, useMemo, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { useNavigate } from "react-router-dom";

// Palette par type de nœud (cohérente avec le design system).
const NODE_COLORS = {
  Artist: "#ff6b4a",
  Recording: "#2dd4bf",
  Release: "#ffb347",
  Genre: "#a78bfa",
  Area: "#60a5fa",
  Label: "#f472b6",
  Unknown: "#9aa0b8",
};

export const GRAPH_LEGEND = [
  { type: "Artist", label: "Artiste" },
  { type: "Recording", label: "Morceau" },
  { type: "Release", label: "Album" },
];

export default function GraphView({ data, height = 560 }) {
  const wrapRef = useRef(null);
  const fgRef = useRef(null);
  const navigate = useNavigate();
  const [width, setWidth] = useState(800);

  // Adapte la largeur du canvas à celle du conteneur.
  useEffect(() => {
    if (!wrapRef.current) return;
    const ro = new ResizeObserver((entries) => {
      setWidth(entries[0].contentRect.width);
    });
    ro.observe(wrapRef.current);
    return () => ro.disconnect();
  }, []);

  // force-graph attend { nodes, links }. On clone pour éviter la mutation des props.
  const graphData = useMemo(
    () => ({
      nodes: (data?.nodes || []).map((n) => ({ ...n })),
      links: (data?.edges || []).map((e) => ({ ...e })),
    }),
    [data]
  );

  return (
    <div className="graph-shell" ref={wrapRef} style={{ height }}>
      <ForceGraph2D
        ref={fgRef}
        width={width}
        height={height}
        graphData={graphData}
        backgroundColor="rgba(0,0,0,0)"
        nodeRelSize={5}
        nodeVal={(n) => (n.type === "Artist" ? 6 : 3)}
        linkColor={(l) =>
          l.type === "SIMILAR_TO"
            ? "rgba(167,139,250,0.28)" // violet = similarité
            : l.type === "COLLABORATED_WITH"
            ? "rgba(255,107,74,0.4)" // coral = collaboration
            : "rgba(45,212,191,0.22)" // teal = autres (performed, appears_on)
        }
        linkWidth={(l) => (l.type === "COLLABORATED_WITH" ? 1.4 : 0.8)}
        linkDirectionalParticles={0}
        cooldownTicks={120}
        onNodeClick={(node) => {
          if (node.type === "Artist") navigate(`/artists/${node.id}`);
        }}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const color = NODE_COLORS[node.type] || NODE_COLORS.Unknown;
          const r = node.type === "Artist" ? 6 : 4;
          ctx.beginPath();
          ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
          ctx.fillStyle = color;
          ctx.shadowColor = color;
          ctx.shadowBlur = node.type === "Artist" ? 12 : 4;
          ctx.fill();
          ctx.shadowBlur = 0;

          // Libellés uniquement pour les artistes (et si assez zoomé).
          if (node.type === "Artist" && globalScale > 1.2) {
            const label = node.label || "";
            ctx.font = `600 ${11 / globalScale + 2}px "Space Grotesk", sans-serif`;
            ctx.textAlign = "center";
            ctx.textBaseline = "top";
            ctx.fillStyle = "#f4f5fb";
            ctx.fillText(label, node.x, node.y + r + 2);
          }
        }}
        nodeLabel={(n) => `${n.label} · ${n.type}`}
      />
      <div className="graph-legend">
        {Object.entries(NODE_COLORS)
          .filter(([t]) => ["Artist", "Recording", "Release"].includes(t))
          .map(([type, color]) => (
            <div className="legend-item" key={type}>
              <span className="legend-swatch" style={{ background: color }} />
              {type === "Artist" ? "Artiste" : type === "Recording" ? "Morceau" : "Album"}
            </div>
          ))}
        <div className="legend-item">
          <span className="legend-swatch" style={{ background: "#ff6b4a", borderRadius: 2, width: 14, height: 3 }} />
          Collaboration
        </div>
        <div className="legend-item">
          <span className="legend-swatch" style={{ background: "#a78bfa", borderRadius: 2, width: 14, height: 3 }} />
          Similaire
        </div>
        <div className="legend-item dim">· clic artiste → fiche</div>
      </div>
    </div>
  );
}
