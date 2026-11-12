
def test_pesquisar_livros_com_sucesso(client, monkeypatch):
    def mock_buscar_livros(termo):
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
                    "capa": "https://exemplo.com/capa.jpg"
                }
            ]
        }

    monkeypatch.setattr(
        "routers.livros.google_books_service.buscar_livros",
        mock_buscar_livros
    )

    resposta = client.get(
        "/livros/pesquisa",
        params={"termo": "O Nome do Vento"}
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
        params={"termo": "A"}
    )

    assert resposta.status_code == 422


def test_pesquisar_livros_com_erro_na_api(client, monkeypatch):
    def mock_buscar_livros(termo):
        raise RuntimeError("Não foi possível conectar à Google Books API.")

    monkeypatch.setattr(
        "routers.livros.google_books_service.buscar_livros",
        mock_buscar_livros
    )

    resposta = client.get(
        "/livros/pesquisa",
        params={"termo": "Harry Potter"}
    )

    assert resposta.status_code == 502
    assert resposta.json()["detail"] == (
        "Não foi possível conectar à Google Books API."
    )
