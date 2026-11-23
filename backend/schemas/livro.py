from pydantic import BaseModel, Field


class LivroPesquisaItem(BaseModel):
    id: str | None = None
    titulo: str | None = None
    autores: list[str] = Field(default_factory=list)
    descricao: str | None = None
    editora: str | None = None
    data_publicacao: str | None = None
    isbn: str | None = None
    capa: str | None = None


class PesquisaLivrosResponse(BaseModel):
    total: int
    livros: list[LivroPesquisaItem]
