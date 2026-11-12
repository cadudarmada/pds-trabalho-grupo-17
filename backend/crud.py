from sqlalchemy.orm import Session

from models import Usuario
from schemas import UsuarioCreate
from security import gerar_hash_senha


def buscar_usuario_por_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email).first()


def criar_usuario(db: Session, usuario: UsuarioCreate) -> Usuario:
    senha_hash = gerar_hash_senha(usuario.senha)

    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=senha_hash
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario