from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import relationship

from core.database import Base


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
    data_adicao = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    usuario = relationship("Usuario", back_populates="livros_biblioteca")
    livro = relationship("Livro", back_populates="usuarios_biblioteca")

    @classmethod
    def criar(cls, usuario_id: int, livro_id: int) -> "UsuarioLivro":
        if usuario_id <= 0:
            raise ValueError("O identificador do usuário deve ser válido.")

        if livro_id <= 0:
            raise ValueError("O identificador do livro deve ser válido.")

        return cls(
            usuario_id=usuario_id,
            livro_id=livro_id,
        )
