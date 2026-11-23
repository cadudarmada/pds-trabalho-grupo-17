class ErroDominio(Exception):
    """Classe base para exceções de negócio e integração da aplicação."""

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem


class EmailJaCadastradoError(ErroDominio):
    def __init__(self, mensagem: str = "Este e-mail já está cadastrado.") -> None:
        super().__init__(mensagem)


class CredenciaisInvalidasError(ErroDominio):
    def __init__(self, mensagem: str = "E-mail ou senha incorretos.") -> None:
        super().__init__(mensagem)


class TokenInvalidoError(ErroDominio):
    def __init__(self, mensagem: str = "Token inválido ou expirado.") -> None:
        super().__init__(mensagem)


class UsuarioNaoEncontradoError(ErroDominio):
    def __init__(self, mensagem: str = "Usuário não encontrado.") -> None:
        super().__init__(mensagem)


class ErroIntegracaoExternaError(ErroDominio):
    """Erro ao se comunicar com uma API externa (ex.: Google Books)."""
