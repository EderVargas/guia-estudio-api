from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str
    db_name: str = "guia-estudio"
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    register_secret_key: str
    frontend_origin: str = "https://edervargas.github.io"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
