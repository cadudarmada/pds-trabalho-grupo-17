import os

import httpx
from dotenv import load_dotenv

load_dotenv()

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")


def buscar_livros(termo: str, max_resultados: int = 10):
    if not GOOGLE_BOOKS_API_KEY:
        raise RuntimeError("Chave da Google Books API não configurada.")

    parametros = {
        "q": termo,
        "key": GOOGLE_BOOKS_API_KEY,
        "maxResults": max_resultados,
        "printType": "books"
    }

    
    try:
        resposta = httpx.get(
            GOOGLE_BOOKS_API_URL,
            params=parametros,
            timeout=15
        )

        resposta.raise_for_status()
        dados = resposta.json()

    except httpx.TimeoutException:
        raise RuntimeError("A pesquisa demorou demais para responder.")

    except httpx.HTTPStatusError:
        raise RuntimeError("A Google Books API retornou um erro.")

    except httpx.RequestError:
        raise RuntimeError("Não foi possível conectar à Google Books API.")

    except ValueError:
        raise RuntimeError("A Google Books API retornou uma resposta inválida.")


    livros = []

    for item in dados.get("items", []):
        volume = item.get("volumeInfo", {})

        identificadores = volume.get("industryIdentifiers", [])

        isbn = next(
            (
                identificador["identifier"]
                for identificador in identificadores
                if identificador.get("type") == "ISBN_13"
            ),
            None
        )

        if not isbn:
            isbn = next(
                (
                    identificador["identifier"]
                    for identificador in identificadores
                    if identificador.get("type") == "ISBN_10"
                ),
                None
            )

        livro = {
            "id": item.get("id"),
            "titulo": volume.get("title"),
            "autores": volume.get("authors", []),
            "descricao": volume.get("description"),
            "editora": volume.get("publisher"),
            "data_publicacao": volume.get("publishedDate"),
            "isbn": isbn,
            "capa": volume.get("imageLinks", {}).get("thumbnail")
        }

        livros.append(livro)

    return {
        "total": dados.get("totalItems", 0),
        "livros": livros
    }
