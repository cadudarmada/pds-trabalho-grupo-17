from core.exceptions import (
    LivroJaNaBibliotecaError,
    LivroNaoEncontradoNaBibliotecaError,
    StatusLeituraInvalidoError,
)
from models.livro import Livro
from models.usuario_livro import StatusLeitura, UsuarioLivro
from repositories.livro_repository import LivroRepository
from repositories.usuario_livro_repository import UsuarioLivroRepository


class BibliotecaService:
    """Orquestra os casos de uso da biblioteca pessoal do usuário."""

    def __init__(
        self,
        livro_repository: LivroRepository,
        usuario_livro_repository: UsuarioLivroRepository,
    ) -> None:
        self._livro_repository = livro_repository
        self._usuario_livro_repository = usuario_livro_repository

    def adicionar_livro(
        self,
        usuario_id: int,
        google_books_id: str,
        titulo: str,
        autores: list[str] | str | None = None,
        editora: str | None = None,
        data_publicacao: str | None = None,
        isbn: str | None = None,
        descricao: str | None = None,
        capa: str | None = None,
    ) -> UsuarioLivro:
        livro = self._livro_repository.buscar_por_google_books_id(google_books_id)

        if livro is None:
            novo_livro = Livro.criar(
                google_books_id=google_books_id,
                titulo=titulo,
                autores=autores,
                editora=editora,
                data_publicacao=data_publicacao,
                isbn=isbn,
                descricao=descricao,
                capa=capa,
            )
            livro = self._livro_repository.criar(novo_livro)

        item_existente = self._usuario_livro_repository.buscar_por_usuario_e_livro(
            usuario_id=usuario_id,
            livro_id=livro.id,
        )

        if item_existente is not None:
            raise LivroJaNaBibliotecaError()

        novo_item = UsuarioLivro.criar(
            usuario_id=usuario_id,
            livro_id=livro.id,
        )

        return self._usuario_livro_repository.criar(novo_item)

    def listar_biblioteca(
        self,
        usuario_id: int,
        status: StatusLeitura | None = None,
    ) -> list[UsuarioLivro]:
        return self._usuario_livro_repository.listar_por_usuario(
            usuario_id=usuario_id,
            status=status,
        )

    def atualizar_status(
        self,
        usuario_id: int,
        usuario_livro_id: int,
        novo_status: StatusLeitura | str,
    ) -> UsuarioLivro:
        item = self._usuario_livro_repository.buscar_por_id_e_usuario(
            usuario_livro_id=usuario_livro_id,
            usuario_id=usuario_id,
        )

        if item is None:
            raise LivroNaoEncontradoNaBibliotecaError()

        try:
            item.atualizar_status(novo_status)
        except ValueError as erro:
            raise StatusLeituraInvalidoError(str(erro)) from erro

        return self._usuario_livro_repository.atualizar(item)
