from fastapi import APIRouter, HTTPException, Query

from services.google_books import GoogleBooksService

router = APIRouter(
    prefix="/livros",
    tags=["Livros"]
)

google_books_service = GoogleBooksService()


@router.get("/pesquisa")
def pesquisar_livros(
    termo: str = Query(
        min_length=2,
        description="Título ou autor do livro que deseja pesquisar"
    )
):
    try:
        resultado = google_books_service.buscar_livros(termo)
        return resultado

    except RuntimeError as erro:
        raise HTTPException(
            status_code=502,
            detail=str(erro)
        )
