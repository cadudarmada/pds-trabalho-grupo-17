from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from core.database import Base


class StatusLeitura(str, Enum):
    QUERO_LER = "QUERO_LER"
    LENDO = "LENDO"
    LIDO = "LIDO"
    ABANDONADO = "ABANDONADO"


class UsuarioLivro(Base):
    __tablename__ = "usuarios_livros"
    __table_args__ = (
        UniqueConstraint("usuario_id", "livro_id", name="uq_usuario_livro"),
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    livro_id = Column(
        Integer,
        ForeignKey("livros.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(
        String(20),
        nullable=False,
        default=StatusLeitura.QUERO_LER.value,
        server_default=StatusLeitura.QUERO_LER.value,
    )
    data_adicao = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    usuario = relationship("Usuario", back_populates="livros_biblioteca")
    livro = relationship("Livro", back_populates="usuarios_biblioteca")

    @staticmethod
    def validar_status(status: StatusLeitura | str) -> StatusLeitura:
        if isinstance(status, StatusLeitura):
            return status

        try:
            return StatusLeitura(status.strip().upper())
        except (AttributeError, ValueError) as erro:
            raise ValueError("Status de leitura inválido.") from erro

    @classmethod
    def criar(
        cls,
        usuario_id: int,
        livro_id: int,
        status: StatusLeitura | str = StatusLeitura.QUERO_LER,
    ) -> "UsuarioLivro":
        if usuario_id <= 0:
            raise ValueError("O identificador do usuário deve ser válido.")

        if livro_id <= 0:
            raise ValueError("O identificador do livro deve ser válido.")

        status_validado = cls.validar_status(status)

        return cls(
            usuario_id=usuario_id,
            livro_id=livro_id,
            status=status_validado.value,
        )

    def atualizar_status(self, novo_status: StatusLeitura | str) -> None:
        status_validado = self.validar_status(novo_status)
        self.status = status_validado.value
