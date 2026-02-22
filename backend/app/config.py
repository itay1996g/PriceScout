from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/pricescout"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    anthropic_api_key: str = ""
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""
    free_search_limit: int = 3
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
