from core.dependencies import get_google_books_client
from core.exceptions import ErroIntegracaoExternaError
from main import app


class FakeGoogleBooksClientSucesso:
    def buscar_volumes(self, termo: str, max_resultados: int = 10) -> dict:
        return {
            "total": 1,
            "livros": [
                {
                    "id": "livro123",
                    "titulo": "O Nome do Vento",
                    "autores": ["Patrick Rothfuss"],
                    "descricao": "A história de Kvothe.",
                    "editora": "Arqueiro",
                    "data_publicacao": "2009",
                    "isbn": "9788599296493",
                    "capa": "https://exemplo.com/capa.jpg",
                }
            ],
        }


class FakeGoogleBooksClientErro:
    def buscar_volumes(self, termo: str, max_resultados: int = 10) -> dict:
        raise ErroIntegracaoExternaError(
            "Não foi possível conectar à Google Books API."
        )


def test_pesquisar_livros_com_sucesso(client):
    app.dependency_overrides[get_google_books_client] = (
        lambda: FakeGoogleBooksClientSucesso()
    )

    resposta = client.get(
        "/livros/pesquisa",
        params={"termo": "O Nome do Vento"},
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["total"] == 1
    assert len(dados["livros"]) == 1
    assert dados["livros"][0]["titulo"] == "O Nome do Vento"
    assert dados["livros"][0]["autores"] == ["Patrick Rothfuss"]


def test_pesquisar_livros_com_termo_curto(client):
    resposta = client.get(
        "/livros/pesquisa",
        params={"termo": "A"},
    )

    assert resposta.status_code == 422


def test_pesquisar_livros_com_erro_na_api(client):
    app.dependency_overrides[get_google_books_client] = (
        lambda: FakeGoogleBooksClientErro()
    )

    resposta = client.get(
        "/livros/pesquisa",
        params={"termo": "Harry Potter"},
    )

    assert resposta.status_code == 502
    assert resposta.json()["detail"] == (
        "Não foi possível conectar à Google Books API."
    )
