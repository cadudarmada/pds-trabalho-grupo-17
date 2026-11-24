from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from core.database import Base
from core.security import PasswordHasher


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    data_criacao = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    livros_biblioteca = relationship(
        "UsuarioLivro",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )

    @staticmethod
    def normalizar_nome(nome: str) -> str:
        nome_limpo = nome.strip()
        if len(nome_limpo) < 3:
            raise ValueError("O nome precisa ter pelo menos 3 caracteres.")
        return nome_limpo

    @staticmethod
    def normalizar_email(email: str) -> str:
        email_limpo = email.strip().lower()
        if not email_limpo or "@" not in email_limpo:
            raise ValueError("E-mail inválido.")
        return email_limpo

    @classmethod
    def criar(cls, nome: str, email: str, senha_hash: str) -> "Usuario":
        if not senha_hash:
            raise ValueError("O hash da senha não pode estar vazio.")

        return cls(
            nome=cls.normalizar_nome(nome),
            email=cls.normalizar_email(email),
            senha_hash=senha_hash,
        )

    def verificar_senha(
        self,
        senha: str,
        password_hasher: PasswordHasher,
    ) -> bool:
        return password_hasher.verificar(senha, self.senha_hash)
