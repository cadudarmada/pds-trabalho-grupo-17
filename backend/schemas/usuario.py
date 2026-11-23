from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        valor = valor.strip()

        if len(valor) < 3:
            raise ValueError("O nome precisa ter pelo menos 3 caracteres.")

        return valor


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class UsuarioAutenticadoResponse(BaseModel):
    mensagem: str
    usuario_id: str
