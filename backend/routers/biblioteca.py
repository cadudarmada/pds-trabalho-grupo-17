from fastapi import APIRouter, Depends, HTTPException, status

from core.dependencies import get_biblioteca_service, get_usuario_atual
from core.exceptions import LivroJaNaBibliotecaError
from models.usuario import Usuario
from schemas.biblioteca import (
    AdicionarLivroBibliotecaRequest,
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
    usuario_atual: Usuario = Depends(get_usuario_atual),
    biblioteca_service: BibliotecaService = Depends(get_biblioteca_service),
):
    itens = biblioteca_service.listar_biblioteca(usuario_atual.id)
    return [ItemBibliotecaResponse.from_entity(item) for item in itens]
