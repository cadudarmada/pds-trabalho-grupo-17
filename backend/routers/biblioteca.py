from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.dependencies import get_biblioteca_service, get_usuario_atual
from core.exceptions import (
    LivroJaNaBibliotecaError,
    LivroNaoEncontradoNaBibliotecaError,
    StatusLeituraInvalidoError,
)
from models.usuario import Usuario
from models.usuario_livro import StatusLeitura
from schemas.biblioteca import (
    AdicionarLivroBibliotecaRequest,
    AtualizarStatusBibliotecaRequest,
    ItemBibliotecaResponse,
)
from services.biblioteca_service import BibliotecaService

router = APIRouter(
    prefix="/biblioteca",
    tags=["Biblioteca"],
)


@router.post(
    "",
    response_model=ItemBibliotecaResponse,
    status_code=status.HTTP_201_CREATED,
)
def adicionar_livro_biblioteca(
    dados: AdicionarLivroBibliotecaRequest,
    usuario_atual: Usuario = Depends(get_usuario_atual),
    biblioteca_service: BibliotecaService = Depends(get_biblioteca_service),
):
    try:
        item = biblioteca_service.adicionar_livro(
            usuario_id=usuario_atual.id,
            google_books_id=dados.google_books_id,
            titulo=dados.titulo,
            autores=dados.autores,
            editora=dados.editora,
            data_publicacao=dados.data_publicacao,
            isbn=dados.isbn,
            descricao=dados.descricao,
            capa=dados.capa,
        )
    except LivroJaNaBibliotecaError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=erro.mensagem,
        )

    return ItemBibliotecaResponse.from_entity(item)


@router.get(
    "",
    response_model=list[ItemBibliotecaResponse],
    status_code=status.HTTP_200_OK,
)
def listar_biblioteca(
    status_leitura: StatusLeitura | None = Query(default=None, alias="status"),
    usuario_atual: Usuario = Depends(get_usuario_atual),
    biblioteca_service: BibliotecaService = Depends(get_biblioteca_service),
):
    itens = biblioteca_service.listar_biblioteca(
        usuario_id=usuario_atual.id,
        status=status_leitura,
    )
    return [ItemBibliotecaResponse.from_entity(item) for item in itens]


@router.patch(
    "/{usuario_livro_id}/status",
    response_model=ItemBibliotecaResponse,
    status_code=status.HTTP_200_OK,
)
def atualizar_status_livro_biblioteca(
    usuario_livro_id: int,
    dados: AtualizarStatusBibliotecaRequest,
    usuario_atual: Usuario = Depends(get_usuario_atual),
    biblioteca_service: BibliotecaService = Depends(get_biblioteca_service),
):
    try:
        item = biblioteca_service.atualizar_status(
            usuario_id=usuario_atual.id,
            usuario_livro_id=usuario_livro_id,
            novo_status=dados.status,
        )
    except LivroNaoEncontradoNaBibliotecaError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=erro.mensagem,
        )
    except StatusLeituraInvalidoError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=erro.mensagem,
        )

    return ItemBibliotecaResponse.from_entity(item)
