import pytest

from core.exceptions import (
    LivroJaNaBibliotecaError,
    LivroNaoEncontradoNaBibliotecaError,
    StatusLeituraInvalidoError,
)
from models.livro import Livro
from models.usuario_livro import StatusLeitura, UsuarioLivro
from services.biblioteca_service import BibliotecaService


class FakeLivroRepository:
    """Repositório de livros em memória para testes unitários."""

    def __init__(self) -> None:
        self._livros: list[Livro] = []
        self._proximo_id = 1

    def buscar_por_id(self, livro_id: int) -> Livro | None:
        return next((livro for livro in self._livros if livro.id == livro_id), None)

    def buscar_por_google_books_id(self, google_books_id: str) -> Livro | None:
        google_id_limpo = google_books_id.strip()
        return next(
            (livro for livro in self._livros if livro.google_books_id == google_id_limpo),
            None,
        )

    def criar(self, livro: Livro) -> Livro:
        livro.id = self._proximo_id
        self._proximo_id += 1
        self._livros.append(livro)
        return livro

    def total(self) -> int:
        return len(self._livros)


class FakeUsuarioLivroRepository:
    """Repositório da biblioteca em memória para testes unitários."""

    def __init__(self) -> None:
        self._itens: list[UsuarioLivro] = []
        self._proximo_id = 1

    def buscar_por_id(self, usuario_livro_id: int) -> UsuarioLivro | None:
        return next(
            (item for item in self._itens if item.id == usuario_livro_id),
            None,
        )

    def buscar_por_id_e_usuario(
        self,
        usuario_livro_id: int,
        usuario_id: int,
    ) -> UsuarioLivro | None:
        return next(
            (
                item
                for item in self._itens
                if item.id == usuario_livro_id and item.usuario_id == usuario_id
            ),
            None,
        )

    def buscar_por_usuario_e_livro(
        self,
        usuario_id: int,
        livro_id: int,
    ) -> UsuarioLivro | None:
        return next(
            (
                item
                for item in self._itens
                if item.usuario_id == usuario_id and item.livro_id == livro_id
            ),
            None,
        )

    def listar_por_usuario(
        self,
        usuario_id: int,
        status: StatusLeitura | None = None,
    ) -> list[UsuarioLivro]:
        itens = [item for item in self._itens if item.usuario_id == usuario_id]
        if status is not None:
            itens = [item for item in itens if item.status == status.value]
        return itens

    def criar(self, usuario_livro: UsuarioLivro) -> UsuarioLivro:
        usuario_livro.id = self._proximo_id
        self._proximo_id += 1
        self._itens.append(usuario_livro)
        return usuario_livro

    def atualizar(self, usuario_livro: UsuarioLivro) -> UsuarioLivro:
        return usuario_livro


def test_adicionar_livro_novo_cria_no_catalogo_e_na_biblioteca():
    livro_repo = FakeLivroRepository()
    biblioteca_repo = FakeUsuarioLivroRepository()
    service = BibliotecaService(livro_repo, biblioteca_repo)

    item = service.adicionar_livro(
        usuario_id=1,
        google_books_id="gb_123",
        titulo="O Nome do Vento",
        autores=["Patrick Rothfuss"],
        editora="Arqueiro",
    )

    assert item.id == 1
    assert item.usuario_id == 1
    assert item.livro_id == 1
    assert item.status == StatusLeitura.QUERO_LER.value
    assert livro_repo.total() == 1


def test_adicionar_livro_ja_existente_no_catalogo_reutiliza_registro():
    livro_repo = FakeLivroRepository()
    biblioteca_repo = FakeUsuarioLivroRepository()
    service = BibliotecaService(livro_repo, biblioteca_repo)

    item_u1 = service.adicionar_livro(
        usuario_id=1,
        google_books_id="gb_duna",
        titulo="Duna",
        autores=["Frank Herbert"],
    )
    item_u2 = service.adicionar_livro(
        usuario_id=2,
        google_books_id="gb_duna",
        titulo="Duna",
        autores=["Frank Herbert"],
    )

    assert livro_repo.total() == 1
    assert item_u1.livro_id == item_u2.livro_id
    assert item_u1.id != item_u2.id


def test_adicionar_livro_duplicado_para_mesmo_usuario_lanca_excecao():
    service = BibliotecaService(
        FakeLivroRepository(),
        FakeUsuarioLivroRepository(),
    )

    service.adicionar_livro(
        usuario_id=1,
        google_books_id="gb_duna",
        titulo="Duna",
    )

    with pytest.raises(LivroJaNaBibliotecaError):
        service.adicionar_livro(
            usuario_id=1,
            google_books_id="gb_duna",
            titulo="Duna",
        )


def test_listar_biblioteca_retorna_apenas_livros_do_usuario():
    service = BibliotecaService(
        FakeLivroRepository(),
        FakeUsuarioLivroRepository(),
    )

    service.adicionar_livro(usuario_id=1, google_books_id="gb_1", titulo="Duna")
    service.adicionar_livro(usuario_id=1, google_books_id="gb_2", titulo="Fundação")
    service.adicionar_livro(usuario_id=2, google_books_id="gb_1", titulo="Duna")

    itens_u1 = service.listar_biblioteca(usuario_id=1)
    itens_u2 = service.listar_biblioteca(usuario_id=2)

    assert len(itens_u1) == 2
    assert len(itens_u2) == 1


def test_atualizar_status_com_sucesso_e_filtrar():
    service = BibliotecaService(
        FakeLivroRepository(),
        FakeUsuarioLivroRepository(),
    )

    item_1 = service.adicionar_livro(usuario_id=1, google_books_id="gb_1", titulo="Duna")
    service.adicionar_livro(usuario_id=1, google_books_id="gb_2", titulo="Fundação")

    atualizado = service.atualizar_status(
        usuario_id=1,
        usuario_livro_id=item_1.id,
        novo_status=StatusLeitura.LENDO,
    )

    assert atualizado.status == StatusLeitura.LENDO.value

    lendo = service.listar_biblioteca(usuario_id=1, status=StatusLeitura.LENDO)
    quero_ler = service.listar_biblioteca(usuario_id=1, status=StatusLeitura.QUERO_LER)

    assert len(lendo) == 1
    assert lendo[0].id == item_1.id
    assert len(quero_ler) == 1


def test_atualizar_status_item_inexistente_ou_de_outro_usuario_lanca_excecao():
    service = BibliotecaService(
        FakeLivroRepository(),
        FakeUsuarioLivroRepository(),
    )

    item_u1 = service.adicionar_livro(usuario_id=1, google_books_id="gb_1", titulo="Duna")

    with pytest.raises(LivroNaoEncontradoNaBibliotecaError):
        service.atualizar_status(usuario_id=1, usuario_livro_id=999, novo_status=StatusLeitura.LIDO)

    with pytest.raises(LivroNaoEncontradoNaBibliotecaError):
        service.atualizar_status(usuario_id=2, usuario_livro_id=item_u1.id, novo_status=StatusLeitura.LIDO)


def test_atualizar_status_invalido_lanca_excecao():
    service = BibliotecaService(
        FakeLivroRepository(),
        FakeUsuarioLivroRepository(),
    )

    item = service.adicionar_livro(usuario_id=1, google_books_id="gb_1", titulo="Duna")

    with pytest.raises(StatusLeituraInvalidoError):
        service.atualizar_status(usuario_id=1, usuario_livro_id=item.id, novo_status="INEXISTENTE")
