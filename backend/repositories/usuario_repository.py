from sqlalchemy.orm import Session

from models import Usuario


class UsuarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def buscar_por_email(self, email: str) -> Usuario | None:
        return self.db.query(Usuario).filter(
            Usuario.email == email
        ).first()

    def criar(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)

        return usuario
