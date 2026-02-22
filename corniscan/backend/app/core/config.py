from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = ""
    jwt_secret: str = "dev-secret-CHANGE-IN-PRODUCTION"
    resend_api_key: str = ""
    resend_from_email: str = "corniscan@cornille-sa.com"
    environment: str = "development"


settings = Settings()
