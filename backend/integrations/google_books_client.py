import httpx

from core.exceptions import ErroIntegracaoExternaError


class GoogleBooksClient:
    """Encapsula a comunicação HTTP externa com a Google Books API."""

    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def __init__(self, api_key: str | None, timeout: int = 15) -> None:
        self._api_key = api_key
        self._timeout = timeout

    def buscar_volumes(self, termo: str, max_resultados: int = 10) -> dict:
        if not self._api_key:
            raise ErroIntegracaoExternaError(
                "Chave da Google Books API não configurada."
            )

        parametros = {
            "q": termo,
            "key": self._api_key,
            "maxResults": max_resultados,
            "printType": "books",
        }

        dados = self._executar_requisicao(parametros)
        livros = [self._mapear_livro(item) for item in dados.get("items", [])]

        return {
            "total": dados.get("totalItems", 0),
            "livros": livros,
        }

    def _executar_requisicao(self, parametros: dict) -> dict:
        try:
            resposta = httpx.get(
                self.BASE_URL,
                params=parametros,
                timeout=self._timeout,
            )
            resposta.raise_for_status()
            return resposta.json()

        except httpx.TimeoutException as erro:
            raise ErroIntegracaoExternaError(
                "A pesquisa demorou demais para responder."
            ) from erro

        except httpx.HTTPStatusError as erro:
            raise ErroIntegracaoExternaError(
                "A Google Books API retornou um erro."
            ) from erro

        except httpx.RequestError as erro:
            raise ErroIntegracaoExternaError(
                "Não foi possível conectar à Google Books API."
            ) from erro

        except ValueError as erro:
            raise ErroIntegracaoExternaError(
                "A Google Books API retornou uma resposta inválida."
            ) from erro

    @staticmethod
    def _extrair_isbn(identificadores: list[dict]) -> str | None:
        for tipo in ("ISBN_13", "ISBN_10"):
            isbn = next(
                (
                    item["identifier"]
                    for item in identificadores
                    if item.get("type") == tipo and item.get("identifier")
                ),
                None,
            )
            if isbn:
                return isbn
        return None

    @classmethod
    def _mapear_livro(cls, item: dict) -> dict:
        volume = item.get("volumeInfo", {})
        identificadores = volume.get("industryIdentifiers", [])

        return {
            "id": item.get("id"),
            "titulo": volume.get("title"),
            "autores": volume.get("authors", []),
            "descricao": volume.get("description"),
            "editora": volume.get("publisher"),
            "data_publicacao": volume.get("publishedDate"),
            "isbn": cls._extrair_isbn(identificadores),
            "capa": volume.get("imageLinks", {}).get("thumbnail"),
        }
