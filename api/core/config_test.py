# api/core/config_test.py

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from api.core.config import Settings


class TestSettings(Settings):
    """
    Test-specific settings class that overrides defaults for the test environment.
    """

    model_config = SettingsConfigDict(
        env_file=None
    )  # No .env for tests; rely on env vars injected by CI

    test_database_url: str = Field(env="TEST_DATABASE_URL")
    testing: bool = True
