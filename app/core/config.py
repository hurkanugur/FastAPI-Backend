from pydantic_settings import BaseSettings

# ==============================
# App settings
# ==============================
class AppSettings(BaseSettings):
    app_name: str
    app_env: str
    app_port: int

    class Config:
        env_file = ".env"
        extra="ignore"


# ==============================
# JWT / Auth settings
# ==============================
class JWTSettings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"
        extra="ignore"


# ==============================
# Database settings
# ==============================
class DBSettings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int

    class Config:
        env_file = ".env"
        extra="ignore"

app_settings = AppSettings()
jwt_settings = JWTSettings()
db_settings = DBSettings()
