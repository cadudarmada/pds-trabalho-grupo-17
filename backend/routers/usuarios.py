from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import UsuarioCreate, UsuarioLogin, UsuarioResponse
from crud import buscar_usuario_por_email, criar_usuario, autenticar_usuario


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
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
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK
)
def login_usuario(
    dados: UsuarioLogin,
    db: Session = Depends(get_db)
):
    usuario = autenticar_usuario(
        db,
        dados.email,
        dados.senha
    )

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    return usuario
