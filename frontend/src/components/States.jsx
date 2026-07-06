export function Loader({ label = "Chargement…" }) {
  return (
    <div className="state">
      <div className="spinner" />
      <span>{label}</span>
    </div>
  );
}

export function ErrorState({ message }) {
  return (
    <div className="state">
      <div className="error-box">⚠️ {message}</div>
    </div>
  );
}

export function EmptyState({ title = "Rien à afficher", hint }) {
  return (
    <div className="state">
      <div style={{ fontSize: "2.5rem" }}>🎧</div>
      <strong style={{ color: "var(--text)" }}>{title}</strong>
      {hint && <span>{hint}</span>}
    </div>
  );
}
