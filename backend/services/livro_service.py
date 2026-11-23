from integrations.google_books_client import GoogleBooksClient


class LivroService:
    """Orquestra os casos de uso relacionados a livros."""

    def __init__(self, google_books_client: GoogleBooksClient) -> None:
        self._google_books_client = google_books_client

    def pesquisar(self, termo: str, max_resultados: int = 10) -> dict:
        termo_limpo = termo.strip()
        return self._google_books_client.buscar_volumes(
            termo=termo_limpo,
            max_resultados=max_resultados,
        )
