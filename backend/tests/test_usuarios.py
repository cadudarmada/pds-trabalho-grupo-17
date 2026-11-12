from security import verificar_senha
from models import Usuario
from database import SessionLocal




def test_cadastrar_usuario_com_sucesso(client):
    resposta = client.post(
        "/usuarios/cadastro",
        json={
            "nome": "Usuario Teste",
            "email": "teste@exemplo.com",
            "senha": "SenhaSegura123"
        }
    )

    assert resposta.status_code == 201

    dados = resposta.json()

    assert dados["nome"] == "Usuario Teste"
    assert dados["email"] == "teste@exemplo.com"
    assert "id" in dados
    assert "data_criacao" in dados
    assert "senha" not in dados
    assert "senha_hash" not in dados

def test_cadastrar_usuario_com_email_duplicado(client):
    dados = {
        "nome": "Usuario Teste",
        "email": "teste@exemplo.com",
        "senha": "SenhaSegura123"
    }

    primeira_resposta = client.post(
        "/usuarios/cadastro",
        json=dados
    )

    segunda_resposta = client.post(
        "/usuarios/cadastro",
        json=dados
    )

    assert primeira_resposta.status_code == 201
    assert segunda_resposta.status_code == 400
    assert segunda_resposta.json()["detail"] == "Este e-mail já está cadastrado."

def test_cadastrar_usuario_com_senha_curta(client):
    resposta = client.post(
        "/usuarios/cadastro",
        json={
            "nome": "Usuario Teste",
            "email": "senha@exemplo.com",
            "senha": "123"
        }
    )

    assert resposta.status_code == 422

def test_cadastrar_usuario_com_email_invalido(client):
    resposta = client.post(
        "/usuarios/cadastro",
        json={
            "nome": "Usuario Teste",
            "email": "email-invalido",
            "senha": "SenhaSegura123"
        }
    )

    assert resposta.status_code == 422

def test_cadastrar_usuario_com_nome_curto(client):
    resposta = client.post(
        "/usuarios/cadastro",
        json={
            "nome": "AB",
            "email": "nome@exemplo.com",
            "senha": "SenhaSegura123"
        }
    )

    assert resposta.status_code == 422

def test_cadastrar_usuario_com_nome_vazio(client):
    resposta = client.post(
        "/usuarios/cadastro",
        json={
            "nome": "   ",
            "email": "vazio@exemplo.com",
            "senha": "SenhaSegura123"
        }
    )

    assert resposta.status_code == 422

def test_cadastrar_usuario_remove_espacos_do_nome(client):
    resposta = client.post(
        "/usuarios/cadastro",
        json={
            "nome": "  Carlos Teste  ",
            "email": "espacos@exemplo.com",
            "senha": "SenhaSegura123"
        }
    )

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Carlos Teste"

def test_senha_e_armazenada_com_hash(client, db_session):
    resposta = client.post(
        "/usuarios/cadastro",
        json={
            "nome": "Usuario Seguro",
            "email": "seguranca@exemplo.com",
            "senha": "SenhaSegura123"
        }
    )

    assert resposta.status_code == 201

    usuario = db_session.query(Usuario).filter(
        Usuario.email == "seguranca@exemplo.com"
    ).first()

    assert usuario is not None
    assert usuario.senha_hash != "SenhaSegura123"

    assert verificar_senha(
        "SenhaSegura123",
        usuario.senha_hash
    )

    assert not verificar_senha(
        "SenhaErrada123",
        usuario.senha_hash
    )


def test_cadastrar_usuario_com_nome_muito_longo(client):
    resposta = client.post(
        "/usuarios/cadastro",
        json={
            "nome": "A" * 101,
            "email": "nome.longo@exemplo.com",
            "senha": "SenhaSegura123"
        }
    )

    assert resposta.status_code == 422


def test_cadastrar_usuario_com_senha_muito_longa(client):
    resposta = client.post(
        "/usuarios/cadastro",
        json={
            "nome": "Usuario Teste",
            "email": "senha.longa@exemplo.com",
            "senha": "A" * 129
        }
    )

    assert resposta.status_code == 422


def test_cadastrar_usuario_sem_nome(client):
    resposta = client.post(
        "/usuarios/cadastro",
        json={
            "email": "sem.nome@exemplo.com",
            "senha": "SenhaSegura123"
        }
    )

    assert resposta.status_code == 422


def test_cadastrar_usuario_sem_email(client):
    resposta = client.post(
        "/usuarios/cadastro",
        json={
            "nome": "Usuario Teste",
            "senha": "SenhaSegura123"
        }
    )

    assert resposta.status_code == 422


def test_cadastrar_usuario_sem_senha(client):
    resposta = client.post(
        "/usuarios/cadastro",
        json={
            "nome": "Usuario Teste",
            "email": "sem.senha@exemplo.com"
        }
    )

    assert resposta.status_code == 422
