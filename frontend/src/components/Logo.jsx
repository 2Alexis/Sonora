// Emblème SONORA : des barres d'égaliseur (le SON) traversées par une arête
// et deux nœuds (le GRAPHE). L'identité du projet en un seul signe.
export function Mark({ size = 34, className = "" }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 40 40"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="sonoraMark" x1="0" y1="1" x2="1" y2="0">
          <stop offset="0" stopColor="#FF6B4A" />
          <stop offset="1" stopColor="#FFB347" />
        </linearGradient>
      </defs>
      {/* Barres d'égaliseur = le son */}
      <g fill="url(#sonoraMark)">
        <rect x="3.5" y="21" width="3.4" height="11" rx="1.7" />
        <rect x="10.5" y="15" width="3.4" height="17" rx="1.7" />
        <rect x="17.3" y="7" width="3.4" height="25" rx="1.7" />
        <rect x="24.3" y="17" width="3.4" height="15" rx="1.7" />
        <rect x="31.2" y="24" width="3.4" height="8" rx="1.7" />
      </g>
      {/* Arête + nœuds = le graphe, posés sur les crêtes */}
      <path d="M12.2 13.5 L26 15.5" stroke="#2DD4BF" strokeWidth="1.5" />
      <circle cx="12.2" cy="13.5" r="3.1" fill="#0B0D17" stroke="#2DD4BF" strokeWidth="1.7" />
      <circle cx="26" cy="15.5" r="3.1" fill="#2DD4BF" />
    </svg>
  );
}

// Logo complet : emblème + typo.
export default function Logo({ size = 30 }) {
  return (
    <span className="brand">
      <Mark size={size} className="brand-mark" />
      <span className="brand-word">
        SON<span className="brand-o">O</span>RA
      </span>
    </span>
  );
}
