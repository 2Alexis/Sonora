// Initiales d'un nom (max 2 lettres) pour les avatars.
export function initials(name = "") {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}

// Durée en ms -> "m:ss".
export function formatDuration(ms) {
  if (!ms || ms <= 0) return "—";
  const total = Math.round(ms / 1000);
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

// Année depuis une date ISO partielle ("2013-05-17" -> "2013").
export function year(date) {
  if (!date) return "—";
  return String(date).slice(0, 4);
}
