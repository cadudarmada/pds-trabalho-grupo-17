from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import relationship

from core.database import Base


class Livro(Base):
    __tablename__ = "livros"

    id = Column(Integer, primary_key=True, index=True)
    google_books_id = Column(String(100), unique=True, nullable=False, index=True)
    titulo = Column(String(255), nullable=False)
    autores = Column(String(500), nullable=True)
    editora = Column(String(255), nullable=True)
    data_publicacao = Column(String(50), nullable=True)
    isbn = Column(String(20), nullable=True, index=True)
    descricao = Column(Text, nullable=True)
    capa = Column(String(500), nullable=True)
    data_criacao = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    usuarios_biblioteca = relationship(
        "UsuarioLivro",
        back_populates="livro",
        cascade="all, delete-orphan",
    )

    @staticmethod
    def normalizar_autores(autores: list[str] | str | None) -> str | None:
        if autores is None:
            return None

        if isinstance(autores, list):
            lista_limpa = [autor.strip() for autor in autores if autor and autor.strip()]
            return ", ".join(lista_limpa) if lista_limpa else None

        texto_limpo = autores.strip()
        return texto_limpo or None

    @classmethod
    def criar(
        cls,
        google_books_id: str,
        titulo: str,
        autores: list[str] | str | None = None,
        editora: str | None = None,
        data_publicacao: str | None = None,
        isbn: str | None = None,
        descricao: str | None = None,
        capa: str | None = None,
    ) -> "Livro":
        google_id_limpo = google_books_id.strip() if google_books_id else ""
        if not google_id_limpo:
            raise ValueError("O identificador do Google Books é obrigatório.")

        titulo_limpo = titulo.strip() if titulo else ""
        if not titulo_limpo:
            raise ValueError("O título do livro é obrigatório.")

        return cls(
            google_books_id=google_id_limpo,
            titulo=titulo_limpo,
            autores=cls.normalizar_autores(autores),
            editora=editora.strip() if editora else None,
            data_publicacao=data_publicacao.strip() if data_publicacao else None,
            isbn=isbn.strip() if isbn else None,
            descricao=descricao.strip() if descricao else None,
            capa=capa.strip() if capa else None,
        )

    def lista_autores(self) -> list[str]:
        if not self.autores:
            return []

        return [autor.strip() for autor in self.autores.split(",") if autor.strip()]
