import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Configuration Vite pour SONORA.
// Le proxy /api évite les soucis de CORS en dev : le front tape sur son propre
// origin (:5173) et Vite relaie vers le backend (:8000).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
