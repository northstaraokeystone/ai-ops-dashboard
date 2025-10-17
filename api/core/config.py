from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized settings class for managing environment variables.

    CRITICAL: The attribute names are now the full environment variable names
    to resolve the Pydantic ValidationError.
    """

    # Use extra='ignore' to avoid errors if other variables are present
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Security Secrets (CRITICAL FIX: Use full NAOK_ name as attribute)
    NAOK_FULCRUM_PRIME_KEY: str
    NAOK_FULCRUM_SALT: str

    # Project Configuration (Adding the critical DATABASE_URL)
    DATABASE_URL: str

    # Defaults
    llm_base_url: str = "https://api.gemini.ai/v1"


settings = Settings()
