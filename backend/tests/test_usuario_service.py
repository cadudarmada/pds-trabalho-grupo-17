import pytest

from core.exceptions import (
    CredenciaisInvalidasError,
    EmailJaCadastradoError,
    UsuarioNaoEncontradoError,
)
from core.security import PasswordHasher, TokenService
from models.usuario import Usuario
from services.usuario_service import UsuarioService


class FakeUsuarioRepository:
    """Repositório em memória para testar UsuarioService sem banco de dados."""

    def __init__(self) -> None:
        self._usuarios: list[Usuario] = []
        self._proximo_id = 1

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        return next(
            (usuario for usuario in self._usuarios if usuario.id == usuario_id),
            None,
        )

    def buscar_por_email(self, email: str) -> Usuario | None:
        email_normalizado = email.strip().lower()
        return next(
            (usuario for usuario in self._usuarios if usuario.email == email_normalizado),
            None,
        )

    def criar(self, usuario: Usuario) -> Usuario:
        usuario.id = self._proximo_id
        self._proximo_id += 1
        self._usuarios.append(usuario)
        return usuario


@pytest.fixture
def usuario_service() -> UsuarioService:
    return UsuarioService(
        usuario_repository=FakeUsuarioRepository(),
        password_hasher=PasswordHasher(),
        token_service=TokenService(
            secret_key="chave-teste-unitaria-com-pelo-menos-32-bytes"
        ),
    )


def test_usuario_criar_normaliza_nome_e_email():
    usuario = Usuario.criar(
        nome="  Ana Silva  ",
        email="  ANA@Exemplo.COM  ",
        senha_hash="hash-simulado",
    )

    assert usuario.nome == "Ana Silva"
    assert usuario.email == "ana@exemplo.com"


def test_usuario_criar_rejeita_nome_curto():
    with pytest.raises(ValueError):
        Usuario.criar(
            nome="  AB  ",
            email="ab@exemplo.com",
            senha_hash="hash-simulado",
        )


def test_usuario_verificar_senha():
    hasher = PasswordHasher()
    usuario = Usuario.criar(
        nome="Carlos",
        email="carlos@exemplo.com",
        senha_hash=hasher.gerar_hash("SenhaSegura123"),
    )

    assert usuario.verificar_senha("SenhaSegura123", hasher) is True
    assert usuario.verificar_senha("OutraSenha", hasher) is False


def test_service_cadastrar_usuario_com_sucesso(usuario_service):
    usuario = usuario_service.cadastrar(
        nome="Maria Clara",
        email="Maria@Exemplo.com",
        senha="SenhaSegura123",
    )

    assert usuario.id == 1
    assert usuario.nome == "Maria Clara"
    assert usuario.email == "maria@exemplo.com"
    assert usuario.senha_hash != "SenhaSegura123"


def test_service_cadastrar_impede_email_duplicado_independente_de_maiusculas(
    usuario_service,
):
    usuario_service.cadastrar(
        nome="Maria Clara",
        email="maria@exemplo.com",
        senha="SenhaSegura123",
    )

    with pytest.raises(EmailJaCadastradoError):
        usuario_service.cadastrar(
            nome="Outra Maria",
            email="MARIA@EXEMPLO.COM",
            senha="OutraSenha123",
        )


def test_service_login_retorna_token_jwt_valido():
    token_service = TokenService(
        secret_key="chave-teste-unitaria-com-pelo-menos-32-bytes"
    )
    service = UsuarioService(
        usuario_repository=FakeUsuarioRepository(),
        password_hasher=PasswordHasher(),
        token_service=token_service,
    )

    usuario = service.cadastrar(
        nome="Joao",
        email="joao@exemplo.com",
        senha="SenhaSegura123",
    )

    token = service.login("joao@exemplo.com", "SenhaSegura123")
    payload = token_service.decodificar_token(token)

    assert payload["sub"] == str(usuario.id)


def test_service_login_com_senha_incorreta_lanca_excecao(usuario_service):
    usuario_service.cadastrar(
        nome="Joao",
        email="joao@exemplo.com",
        senha="SenhaSegura123",
    )

    with pytest.raises(CredenciaisInvalidasError):
        usuario_service.login("joao@exemplo.com", "SenhaErrada")


def test_service_buscar_por_id_inexistente_lanca_excecao(usuario_service):
    with pytest.raises(UsuarioNaoEncontradoError):
        usuario_service.buscar_por_id(999)
