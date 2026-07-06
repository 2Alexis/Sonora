"""Configuration centrale de SONORA (chargée depuis les variables d'environnement)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres de l'application, injectés via le fichier .env / docker-compose."""

    # --- Identité applicative ---
    app_name: str = "SONORA"
    app_env: str = "development"
    api_prefix: str = "/api"

    # --- Neo4j ---
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "sonora_dev_password"
    neo4j_database: str = "neo4j"

    # --- MusicBrainz ---
    # MusicBrainz IMPOSE un User-Agent identifiable + max 1 requête / seconde.
    musicbrainz_base_url: str = "https://musicbrainz.org/ws/2"
    musicbrainz_user_agent: str = "SONORA/1.0 (https://github.com/your-org/sonora)"
    musicbrainz_rate_limit_seconds: float = 1.1  # marge de sécurité au-dessus de 1s
    musicbrainz_timeout_seconds: float = 15.0
    musicbrainz_max_retries: int = 3

    # --- Deezer (enrichissement : image, fans, similaires, previews) ---
    # API publique sans authentification.
    deezer_base_url: str = "https://api.deezer.com"
    deezer_rate_limit_seconds: float = 0.2
    deezer_timeout_seconds: float = 12.0

    # --- Last.fm (enrichissement : similaires, auditeurs, tags) ---
    # OPTIONNEL : sans clé, l'enrichissement Last.fm est simplement ignoré.
    lastfm_api_key: str = ""
    lastfm_base_url: str = "https://ws.audioscrobbler.com/2.0/"
    lastfm_rate_limit_seconds: float = 0.25
    lastfm_timeout_seconds: float = 12.0

    # --- Enrichissement ---
    enrichment_enabled: bool = True
    similar_max_per_artist: int = 20

    # --- Limites d'import (qualité + politesse envers l'API) ---
    import_max_recordings: int = 25
    import_max_releases_per_recording: int = 3

    # --- CORS (frontend Vite) ---
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Retourne un singleton de configuration (cache pour éviter de relire l'env)."""
    return Settings()


settings = get_settings()
