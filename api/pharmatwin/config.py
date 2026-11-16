"""Runtime settings. Model ids and secrets come from the environment only."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(ROOT / ".env"), str(ROOT / ".env.example")),
        extra="ignore",
    )

    openrouter_api_key: str = ""
    openrouter_model: str = ""
    openrouter_fallback_models: str = ""
    app_url: str = "http://localhost:3000"
    database_url: str = "sqlite:///./pharmatwin.db"
    sim_runs: int = 200
    sim_horizon_days: int = 90
    sim_seed: int = 42
    demo_password: str = ""
    next_public_api_url: str = "http://localhost:8000"

    @property
    def fallback_models(self) -> list[str]:
        return [item.strip() for item in self.openrouter_fallback_models.split(",") if item.strip()]

    @property
    def resolved_database_url(self) -> str:
        prefix = "sqlite:///./"
        if self.database_url.startswith(prefix):
            path = (ROOT / self.database_url.removeprefix(prefix)).resolve()
            return "sqlite:///" + path.as_posix()
        if self.database_url.startswith("sqlite:///") and not self.database_url.startswith("sqlite:////"):
            raw = self.database_url.removeprefix("sqlite:///")
            path = Path(raw)
            if not path.is_absolute():
                path = (ROOT / path).resolve()
            return "sqlite:///" + path.as_posix()
        return self.database_url


def get_settings() -> Settings:
    return Settings()
