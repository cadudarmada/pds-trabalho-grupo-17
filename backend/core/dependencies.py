from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from core.exceptions import TokenInvalidoError, UsuarioNaoEncontradoError
from core.security import PasswordHasher, TokenService
from integrations.google_books_client import GoogleBooksClient
from models.usuario import Usuario
from repositories.livro_repository import LivroRepository
from repositories.usuario_livro_repository import UsuarioLivroRepository
from repositories.usuario_repository import UsuarioRepository
from services.biblioteca_service import BibliotecaService
from services.livro_service import LivroService
from services.usuario_service import UsuarioService

bearer_scheme = HTTPBearer()
_password_hasher = PasswordHasher()


def get_password_hasher() -> PasswordHasher:
    return _password_hasher


def get_token_service() -> TokenService:
    return TokenService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expire_minutes=settings.jwt_expire_minutes,
    )


def get_usuario_repository(
    db: Session = Depends(get_db),
) -> UsuarioRepository:
    return UsuarioRepository(db)


def get_usuario_service(
    usuario_repository: UsuarioRepository = Depends(get_usuario_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
) -> UsuarioService:
    return UsuarioService(
        usuario_repository=usuario_repository,
        password_hasher=password_hasher,
        token_service=token_service,
    )


def get_google_books_client() -> GoogleBooksClient:
    return GoogleBooksClient(
        api_key=settings.google_books_api_key,
        timeout=settings.google_books_timeout,
    )


def get_livro_service(
    google_books_client: GoogleBooksClient = Depends(get_google_books_client),
) -> LivroService:
    return LivroService(google_books_client=google_books_client)


def get_livro_repository(
    db: Session = Depends(get_db),
) -> LivroRepository:
    return LivroRepository(db)


def get_usuario_livro_repository(
    db: Session = Depends(get_db),
) -> UsuarioLivroRepository:
    return UsuarioLivroRepository(db)


def get_biblioteca_service(
    livro_repository: LivroRepository = Depends(get_livro_repository),
    usuario_livro_repository: UsuarioLivroRepository = Depends(
        get_usuario_livro_repository
    ),
) -> BibliotecaService:
    return BibliotecaService(
        livro_repository=livro_repository,
        usuario_livro_repository=usuario_livro_repository,
    )


def get_usuario_atual(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    token_service: TokenService = Depends(get_token_service),
    usuario_service: UsuarioService = Depends(get_usuario_service),
) -> Usuario:
    try:
        payload = token_service.decodificar_token(credentials.credentials)
    except TokenInvalidoError as erro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=erro.mensagem,
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não contém identificação do usuário.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        usuario_id = int(sub)
        return usuario_service.buscar_por_id(usuario_id)
    except (ValueError, UsuarioNaoEncontradoError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário do token não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
