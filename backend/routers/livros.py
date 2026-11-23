from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.dependencies import get_livro_service
from core.exceptions import ErroIntegracaoExternaError
from schemas.livro import PesquisaLivrosResponse
from services.livro_service import LivroService

router = APIRouter(
    prefix="/livros",
    tags=["Livros"],
)


@router.get("/pesquisa", response_model=PesquisaLivrosResponse)
def pesquisar_livros(
    termo: str = Query(
        min_length=2,
        description="Título ou autor do livro que deseja pesquisar",
    ),
    livro_service: LivroService = Depends(get_livro_service),
):
    try:
        return livro_service.pesquisar(termo)
    except ErroIntegracaoExternaError as erro:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=erro.mensagem,
        )
