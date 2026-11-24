from sqlalchemy.orm import Session

from models.livro import Livro


class LivroRepository:
    """Encapsula as operações de persistência da entidade Livro."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def buscar_por_id(self, livro_id: int) -> Livro | None:
        return (
            self._db.query(Livro)
            .filter(Livro.id == livro_id)
            .first()
        )

    def buscar_por_google_books_id(self, google_books_id: str) -> Livro | None:
        google_id_limpo = google_books_id.strip()
        return (
            self._db.query(Livro)
            .filter(Livro.google_books_id == google_id_limpo)
            .first()
        )

    def criar(self, livro: Livro) -> Livro:
        self._db.add(livro)
        self._db.commit()
        self._db.refresh(livro)
        return livro
