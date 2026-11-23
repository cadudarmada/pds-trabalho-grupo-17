from sqlalchemy.orm import Session

from core.security import PasswordHasher
from models.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository
from schemas import UsuarioCreate

password_hasher = PasswordHasher()


def buscar_usuario_por_email(db: Session, email: str) -> Usuario | None:
    return UsuarioRepository(db).buscar_por_email(email)


def criar_usuario(db: Session, usuario: UsuarioCreate) -> Usuario:
    senha_hash = password_hasher.gerar_hash(usuario.senha)

    novo_usuario = Usuario.criar(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=senha_hash,
    )

    return UsuarioRepository(db).criar(novo_usuario)


def autenticar_usuario(db: Session, email: str, senha: str) -> Usuario | None:
    usuario = UsuarioRepository(db).buscar_por_email(email)

    if usuario is None:
        return None

    if not usuario.verificar_senha(senha, password_hasher):
        return None

    return usuario