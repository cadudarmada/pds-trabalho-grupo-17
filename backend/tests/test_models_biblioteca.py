import pytest
from sqlalchemy.exc import IntegrityError

from models.livro import Livro
from models.usuario import Usuario
from models.usuario_livro import UsuarioLivro


def test_livro_criar_normaliza_campos_e_lista_autores():
    livro = Livro.criar(
        google_books_id="  gb_123  ",
        titulo="  O Nome do Vento  ",
        autores=[" Patrick Rothfuss ", "  "],
        editora="  Arqueiro  ",
        data_publicacao=" 2009 ",
        isbn=" 9788599296493 ",
        descricao="  História de Kvothe.  ",
        capa=" https://exemplo.com/capa.jpg ",
    )

    assert livro.google_books_id == "gb_123"
    assert livro.titulo == "O Nome do Vento"
    assert livro.autores == "Patrick Rothfuss"
    assert livro.lista_autores() == ["Patrick Rothfuss"]
    assert livro.editora == "Arqueiro"
    assert livro.data_publicacao == "2009"
    assert livro.isbn == "9788599296493"


def test_livro_criar_rejeita_google_books_id_vazio():
    with pytest.raises(ValueError):
        Livro.criar(google_books_id="   ", titulo="Duna")


def test_livro_criar_rejeita_titulo_vazio():
    with pytest.raises(ValueError):
        Livro.criar(google_books_id="gb_456", titulo="   ")


def test_usuario_livro_criar_rejeita_ids_invalidos():
    with pytest.raises(ValueError):
        UsuarioLivro.criar(usuario_id=0, livro_id=1)

    with pytest.raises(ValueError):
        UsuarioLivro.criar(usuario_id=1, livro_id=-2)


def test_relacionamento_e_unicidade_na_biblioteca(db_session):
    usuario_1 = Usuario.criar("Ana Silva", "ana@exemplo.com", "hash1")
    usuario_2 = Usuario.criar("Bruno Lima", "bruno@exemplo.com", "hash2")
    livro = Livro.criar(
        google_books_id="gb_duna",
        titulo="Duna",
        autores=["Frank Herbert"],
    )

    db_session.add_all([usuario_1, usuario_2, livro])
    db_session.commit()

    item_u1 = UsuarioLivro.criar(usuario_id=usuario_1.id, livro_id=livro.id)
    item_u2 = UsuarioLivro.criar(usuario_id=usuario_2.id, livro_id=livro.id)

    db_session.add_all([item_u1, item_u2])
    db_session.commit()

    db_session.refresh(usuario_1)
    assert len(usuario_1.livros_biblioteca) == 1
    assert usuario_1.livros_biblioteca[0].livro.titulo == "Duna"

    duplicado = UsuarioLivro.criar(usuario_id=usuario_1.id, livro_id=livro.id)
    db_session.add(duplicado)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
