from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from core.exceptions import TokenInvalidoError


class PasswordHasher:
    """Encapsula a geração e verificação de hash de senhas com Argon2."""

    def __init__(self) -> None:
        self._hasher = PasswordHash.recommended()

    def gerar_hash(self, senha: str) -> str:
        return self._hasher.hash(senha)

    def verificar(self, senha: str, senha_hash: str) -> bool:
        return self._hasher.verify(senha, senha_hash)


class TokenService:
    """Responsável por gerar e validar tokens JWT de acesso."""

    def __init__(
        self,
        secret_key: str | None,
        algorithm: str = "HS256",
        expire_minutes: int = 60,
    ) -> None:
        if not secret_key:
            raise RuntimeError("A variável JWT_SECRET_KEY não foi configurada.")

        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    def criar_access_token(self, usuario_id: int) -> str:
        expiracao = datetime.now(timezone.utc) + timedelta(
            minutes=self._expire_minutes
        )

        payload = {
            "sub": str(usuario_id),
            "exp": expiracao,
        }

        return jwt.encode(
            payload,
            self._secret_key,
            algorithm=self._algorithm,
        )

    def decodificar_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
            )
        except jwt.InvalidTokenError as erro:
            raise TokenInvalidoError() from erro
