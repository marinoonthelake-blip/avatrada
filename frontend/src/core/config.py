from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "AVATRADA 1.0 DIAMOND"
    APP_ENV: str = "paper"
    TZ: str = "UTC" # Default to UTC if missing

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    # IBKR
    IBKR_HOST: str = "ib-gateway"
    IBKR_PORT: int = 4004
    IBKR_ACCOUNT: str

    # ThetaData
    THETA_HOST: str = "theta-terminal"
    THETA_PORT: int = 25503 
    THETA_USERNAME: str
    THETA_PASSWORD: str

    # AI Keys
    GOOGLE_API_KEY_1: str
    GOOGLE_API_KEY_2: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
