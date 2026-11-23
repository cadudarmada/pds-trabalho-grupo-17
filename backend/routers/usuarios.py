from fastapi import APIRouter, Depends, HTTPException, status

from core.dependencies import get_usuario_atual, get_usuario_service
from core.exceptions import CredenciaisInvalidasError, EmailJaCadastradoError
from models.usuario import Usuario
from schemas.usuario import (
    Token,
    UsuarioAutenticadoResponse,
    UsuarioCreate,
    UsuarioLogin,
    UsuarioResponse,
)
from services.usuario_service import UsuarioService

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"],
)


@router.post(
    "/cadastro",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_usuario(
    dados: UsuarioCreate,
    usuario_service: UsuarioService = Depends(get_usuario_service),
):
    try:
        return usuario_service.cadastrar(
            nome=dados.nome,
            email=dados.email,
            senha=dados.senha,
        )
    except EmailJaCadastradoError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=erro.mensagem,
        )


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
)
def login_usuario(
    dados: UsuarioLogin,
    usuario_service: UsuarioService = Depends(get_usuario_service),
):
    try:
        access_token = usuario_service.login(
            email=dados.email,
            senha=dados.senha,
        )
    except CredenciaisInvalidasError as erro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=erro.mensagem,
        )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UsuarioAutenticadoResponse)
def obter_usuario_autenticado(
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    return UsuarioAutenticadoResponse(
        mensagem="Token válido.",
        usuario_id=str(usuario_atual.id),
    )
