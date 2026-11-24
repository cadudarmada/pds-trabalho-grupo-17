from sqlalchemy.orm import Session, joinedload

from models.usuario_livro import StatusLeitura, UsuarioLivro


class UsuarioLivroRepository:
    """Encapsula as operações de persistência da biblioteca pessoal."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def buscar_por_id(self, usuario_livro_id: int) -> UsuarioLivro | None:
        return (
            self._db.query(UsuarioLivro)
            .options(joinedload(UsuarioLivro.livro))
            .filter(UsuarioLivro.id == usuario_livro_id)
            .first()
        )

    def buscar_por_id_e_usuario(
        self,
        usuario_livro_id: int,
        usuario_id: int,
    ) -> UsuarioLivro | None:
        return (
            self._db.query(UsuarioLivro)
            .options(joinedload(UsuarioLivro.livro))
            .filter(
                UsuarioLivro.id == usuario_livro_id,
                UsuarioLivro.usuario_id == usuario_id,
            )
            .first()
        )

    def buscar_por_usuario_e_livro(
        self,
        usuario_id: int,
        livro_id: int,
    ) -> UsuarioLivro | None:
        return (
            self._db.query(UsuarioLivro)
            .options(joinedload(UsuarioLivro.livro))
            .filter(
                UsuarioLivro.usuario_id == usuario_id,
                UsuarioLivro.livro_id == livro_id,
            )
            .first()
        )

    def listar_por_usuario(
        self,
        usuario_id: int,
        status: StatusLeitura | None = None,
    ) -> list[UsuarioLivro]:
        consulta = (
            self._db.query(UsuarioLivro)
            .options(joinedload(UsuarioLivro.livro))
            .filter(UsuarioLivro.usuario_id == usuario_id)
        )

        if status is not None:
            consulta = consulta.filter(UsuarioLivro.status == status.value)

        return (
            consulta
            .order_by(UsuarioLivro.data_adicao.desc(), UsuarioLivro.id.desc())
            .all()
        )

    def criar(self, usuario_livro: UsuarioLivro) -> UsuarioLivro:
        self._db.add(usuario_livro)
        self._db.commit()
        self._db.refresh(usuario_livro)
        return usuario_livro

    def atualizar(self, usuario_livro: UsuarioLivro) -> UsuarioLivro:
        self._db.add(usuario_livro)
        self._db.commit()
        self._db.refresh(usuario_livro)
        return usuario_livro
