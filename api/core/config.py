from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized settings class for managing environment variables.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    naok_fulcrum_prime_key: str
    naok_fulcrum_salt: str
    llm_base_url: str = "https://api.gemini.ai/v1"


settings = Settings()
