from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor):
        valor = valor.strip()

        if not valor:
            raise ValueError("O nome não pode estar vazio.")

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