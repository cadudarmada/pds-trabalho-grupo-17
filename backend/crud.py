from sqlalchemy.orm import Session

from models import Usuario
from schemas import UsuarioCreate
from core.security import PasswordHasher

password_hasher = PasswordHasher()


def buscar_usuario_por_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email).first()


def criar_usuario(db: Session, usuario: UsuarioCreate) -> Usuario:
    senha_hash = password_hasher.gerar_hash(usuario.senha)

    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=senha_hash
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario

def autenticar_usuario(db: Session, email: str, senha: str) -> Usuario | None:
    usuario = buscar_usuario_por_email(db, email)

    if usuario is None:
        return None

    if not password_hasher.verificar(senha, usuario.senha_hash):
        return None

    return usuario