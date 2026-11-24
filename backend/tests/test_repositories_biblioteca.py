from models.livro import Livro
from models.usuario import Usuario
from models.usuario_livro import UsuarioLivro
from repositories.livro_repository import LivroRepository
from repositories.usuario_livro_repository import UsuarioLivroRepository
from repositories.usuario_repository import UsuarioRepository


def test_livro_repository_criar_e_buscar(db_session):
    repo = LivroRepository(db_session)

    livro = Livro.criar(
        google_books_id="gb_001",
        titulo="O Nome do Vento",
        autores=["Patrick Rothfuss"],
        editora="Arqueiro",
    )

    criado = repo.criar(livro)

    assert criado.id is not None
    assert repo.buscar_por_id(criado.id).titulo == "O Nome do Vento"
    assert repo.buscar_por_google_books_id("  gb_001  ").id == criado.id
    assert repo.buscar_por_google_books_id("inexistente") is None


def test_usuario_livro_repository_criar_buscar_e_listar(db_session):
    usuario_repo = UsuarioRepository(db_session)
    livro_repo = LivroRepository(db_session)
    biblioteca_repo = UsuarioLivroRepository(db_session)

    usuario_1 = usuario_repo.criar(Usuario.criar("Ana Silva", "ana@exemplo.com", "hash1"))
    usuario_2 = usuario_repo.criar(Usuario.criar("Bruno Lima", "bruno@exemplo.com", "hash2"))

    livro_1 = livro_repo.criar(Livro.criar(google_books_id="gb_1", titulo="Duna"))
    livro_2 = livro_repo.criar(Livro.criar(google_books_id="gb_2", titulo="Fundação"))

    item_1 = biblioteca_repo.criar(UsuarioLivro.criar(usuario_1.id, livro_1.id))
    item_2 = biblioteca_repo.criar(UsuarioLivro.criar(usuario_1.id, livro_2.id))
    biblioteca_repo.criar(UsuarioLivro.criar(usuario_2.id, livro_1.id))

    encontrado_id = biblioteca_repo.buscar_por_id(item_1.id)
    assert encontrado_id is not None
    assert encontrado_id.livro.titulo == "Duna"

    encontrado_par = biblioteca_repo.buscar_por_usuario_e_livro(usuario_1.id, livro_2.id)
    assert encontrado_par is not None
    assert encontrado_par.id == item_2.id

    assert biblioteca_repo.buscar_por_usuario_e_livro(usuario_2.id, livro_2.id) is None

    lista_u1 = biblioteca_repo.listar_por_usuario(usuario_1.id)
    assert [item.livro.titulo for item in lista_u1] == ["Fundação", "Duna"]

    lista_u2 = biblioteca_repo.listar_por_usuario(usuario_2.id)
    assert [item.livro.titulo for item in lista_u2] == ["Duna"]
