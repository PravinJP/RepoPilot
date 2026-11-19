from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "RepoPilot Core"
    debug: bool = False
    database_url: str = "postgresql+psycopg://repopilot:repopilot_dev@127.0.0.1:5433/repopilot"

settings = Settings()