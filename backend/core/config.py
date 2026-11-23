import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Centraliza as configurações da aplicação carregadas do ambiente."""

    def __init__(self) -> None:
        self.db_host = os.getenv("DB_HOST")
        self.db_port = os.getenv("DB_PORT")
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")

        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

        self.google_books_api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
        self.google_books_timeout = int(os.getenv("GOOGLE_BOOKS_TIMEOUT", "15"))

    @property
    def database_url(self) -> str:
        if not all([self.db_host, self.db_port, self.db_name, self.db_user, self.db_password]):
            raise RuntimeError(
                "Variáveis de ambiente do banco de dados não configuradas."
            )

        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
