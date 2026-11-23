from core.exceptions import (
    CredenciaisInvalidasError,
    EmailJaCadastradoError,
    UsuarioNaoEncontradoError,
)
from core.security import PasswordHasher, TokenService
from models.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository


class UsuarioService:
    """Orquestra os casos de uso relacionados a usuários e autenticação."""

    def __init__(
        self,
        usuario_repository: UsuarioRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._usuario_repository = usuario_repository
        self._password_hasher = password_hasher
        self._token_service = token_service

    def cadastrar(self, nome: str, email: str, senha: str) -> Usuario:
        usuario_existente = self._usuario_repository.buscar_por_email(email)

        if usuario_existente is not None:
            raise EmailJaCadastradoError()

        senha_hash = self._password_hasher.gerar_hash(senha)
        novo_usuario = Usuario.criar(
            nome=nome,
            email=email,
            senha_hash=senha_hash,
        )

        return self._usuario_repository.criar(novo_usuario)

    def autenticar(self, email: str, senha: str) -> Usuario:
        usuario = self._usuario_repository.buscar_por_email(email)

        if usuario is None or not usuario.verificar_senha(senha, self._password_hasher):
            raise CredenciaisInvalidasError()

        return usuario

    def login(self, email: str, senha: str) -> str:
        usuario = self.autenticar(email, senha)
        return self._token_service.criar_access_token(usuario.id)

    def buscar_por_id(self, usuario_id: int) -> Usuario:
        usuario = self._usuario_repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise UsuarioNaoEncontradoError()

        return usuario
