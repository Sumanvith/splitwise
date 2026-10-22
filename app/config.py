from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str        # postgresql+asyncpg://... (app)
    sync_database_url: str   # postgresql+psycopg2://... (Alembic only)
    secret_key: str
    project_name: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    redis_url: str


settings = Settings()
