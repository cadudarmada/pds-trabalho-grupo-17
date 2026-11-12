
from sqlalchemy.orm import Session

from models import Usuario
from schemas import UsuarioCreate
from security import gerar_hash_senha, verificar_senha
from repositories.usuario_repository import UsuarioRepository


class UsuarioService:

    def __init__(self, db: Session):
        self.usuario_repository = UsuarioRepository(db)

    def buscar_por_email(self, email: str) -> Usuario | None:
        return self.usuario_repository.buscar_por_email(email)

    def cadastrar(self, dados: UsuarioCreate) -> Usuario:
        senha_hash = gerar_hash_senha(dados.senha)

        novo_usuario = Usuario(
            nome=dados.nome,
            email=dados.email,
            senha_hash=senha_hash
        )

        return self.usuario_repository.criar(novo_usuario)

    def autenticar(self, email: str, senha: str) -> Usuario | None:
        usuario = self.usuario_repository.buscar_por_email(email)

        if usuario is None:
            return None

        if not verificar_senha(senha, usuario.senha_hash):
            return None

        return usuario
