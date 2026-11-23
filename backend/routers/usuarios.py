from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from core.exceptions import TokenInvalidoError
from core.security import TokenService
from schemas import UsuarioCreate, UsuarioLogin, UsuarioResponse, Token
from crud import buscar_usuario_por_email, criar_usuario, autenticar_usuario

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)

bearer_scheme = HTTPBearer()


def _obter_token_service() -> TokenService:
    return TokenService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expire_minutes=settings.jwt_expire_minutes,
    )

@router.post(
    "/cadastro",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED
)
def cadastrar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    usuario_existente = buscar_usuario_por_email(db, usuario.email)

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este e-mail já está cadastrado."
        )

    novo_usuario = criar_usuario(db, usuario)

    return novo_usuario

@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK
)
def login_usuario(
    dados: UsuarioLogin,
    db: Session = Depends(get_db)
):
    usuario = autenticar_usuario(db, dados.email, dados.senha)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    token_service = _obter_token_service()
    access_token = token_service.criar_access_token(usuario.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
def obter_usuario_autenticado(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    token_service = _obter_token_service()

    try:
        payload = token_service.decodificar_token(credentials.credentials)
    except TokenInvalidoError as erro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=erro.mensagem,
            headers={"WWW-Authenticate": "Bearer"}
        )

    usuario_id = payload.get("sub")

    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não contém identificação do usuário."
        )

    return {
        "mensagem": "Token válido.",
        "usuario_id": usuario_id
    }