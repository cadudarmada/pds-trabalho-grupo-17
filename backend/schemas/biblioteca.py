from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from models.usuario_livro import UsuarioLivro


class AdicionarLivroBibliotecaRequest(BaseModel):
    google_books_id: str = Field(min_length=1, max_length=100)
    titulo: str = Field(min_length=1, max_length=255)
    autores: list[str] = Field(default_factory=list)
    editora: str | None = Field(default=None, max_length=255)
    data_publicacao: str | None = Field(default=None, max_length=50)
    isbn: str | None = Field(default=None, max_length=20)
    descricao: str | None = None
    capa: str | None = Field(default=None, max_length=500)

    @field_validator("google_books_id", "titulo")
    @classmethod
    def validar_texto_obrigatorio(cls, valor: str) -> str:
        valor_limpo = valor.strip()
        if not valor_limpo:
            raise ValueError("Este campo não pode estar vazio.")
        return valor_limpo


class LivroBibliotecaResponse(BaseModel):
    id: int
    google_books_id: str
    titulo: str
    autores: list[str] = Field(default_factory=list)
    editora: str | None = None
    data_publicacao: str | None = None
    isbn: str | None = None
    descricao: str | None = None
    capa: str | None = None


class ItemBibliotecaResponse(BaseModel):
    id: int
    data_adicao: datetime
    livro: LivroBibliotecaResponse

    @classmethod
    def from_entity(cls, item: UsuarioLivro) -> "ItemBibliotecaResponse":
        livro = item.livro
        return cls(
            id=item.id,
            data_adicao=item.data_adicao,
            livro=LivroBibliotecaResponse(
                id=livro.id,
                google_books_id=livro.google_books_id,
                titulo=livro.titulo,
                autores=livro.lista_autores(),
                editora=livro.editora,
                data_publicacao=livro.data_publicacao,
                isbn=livro.isbn,
                descricao=livro.descricao,
                capa=livro.capa,
            ),
        )
