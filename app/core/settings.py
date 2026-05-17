from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Python Backend API"
    app_version: str = "1.0.0"
    debug: bool = False
    app_timezone: str = "America/Mexico_City"
    jwt_secret_key: str = "change-this-secret-to-a-very-long-random-value"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_minutes: int = 60

    # Full override URL. If set, this value is used directly.
    database_url: str | None = None

    # Discrete DB settings (used when DATABASE_URL is not set).
    db_scheme: str = "mariadb+mariadbconnector"
    db_host: str | None = None
    db_port: int | None = None
    db_database: str | None = None
    db_username: str | None = None
    db_password: str | None = None
    db_timezone: str = "-06:00"

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        if all([self.db_host, self.db_port, self.db_database, self.db_username, self.db_password]):
            username = quote_plus(str(self.db_username))
            password = quote_plus(str(self.db_password))
            return f"{self.db_scheme}://{username}:{password}@{self.db_host}:{self.db_port}/{self.db_database}"

        return "sqlite:///./app.db"

    # Email SMTP settings
    mail_mailer: str = "smtp"
    mail_scheme: str = "smtp"
    mail_host: str = "localhost"
    mail_port: int = 1025
    mail_username: str | None = None
    mail_password: str | None = None
    mail_from_address: str | None = None
    mail_from_name: str = "Python Backend API"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
