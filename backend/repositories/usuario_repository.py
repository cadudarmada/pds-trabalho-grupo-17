from sqlalchemy.orm import Session

from models.usuario import Usuario


class UsuarioRepository:
    """Encapsula as operações de persistência da entidade Usuario."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        return (
            self._db.query(Usuario)
            .filter(Usuario.id == usuario_id)
            .first()
        )

    def buscar_por_email(self, email: str) -> Usuario | None:
        email_normalizado = email.strip().lower()
        return (
            self._db.query(Usuario)
            .filter(Usuario.email == email_normalizado)
            .first()
        )

    def criar(self, usuario: Usuario) -> Usuario:
        self._db.add(usuario)
        self._db.commit()
        self._db.refresh(usuario)
        return usuario
