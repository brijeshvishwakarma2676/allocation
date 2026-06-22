from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Allocation API"
    VERSION: str = "1.0.0"
    PORT: int = 8000
    IS_PROD: bool = False

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "allocation_db"

    # Logging
    APP_LOG_FILE: str = "logs/app.log"
    APP_LOG_ARCHIVE_DIR: str = "logs/log_archive"
    APP_LOG_MAX_BYTES: int = 20 * 1024 * 1024   # 20 MB

    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"

settings = Settings()
