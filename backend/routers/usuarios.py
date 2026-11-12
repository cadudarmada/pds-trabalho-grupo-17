from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from schemas import UsuarioCreate, UsuarioLogin, UsuarioResponse, Token
from services.usuario_service import UsuarioService
from jwt_utils import criar_access_token, verificar_access_token

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)

bearer_scheme = HTTPBearer()


@router.post(
    "/cadastro",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED
)
def cadastrar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    usuario_service = UsuarioService(db)

    usuario_existente = usuario_service.buscar_por_email(usuario.email)

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este e-mail já está cadastrado."
        )

    novo_usuario = usuario_service.cadastrar(usuario)

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
    usuario_service = UsuarioService(db)

    usuario = usuario_service.autenticar(dados.email, dados.senha)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    access_token = criar_access_token(
        dados={"sub": str(usuario.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me")
def obter_usuario_autenticado(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    payload = verificar_access_token(credentials.credentials)

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
