from core.security import PasswordHasher
from models.usuario import Usuario




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

    hasher = PasswordHasher()

    assert hasher.verificar(
        "SenhaSegura123",
        usuario.senha_hash
    )

    assert not hasher.verificar(
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


def test_login_usuario_com_sucesso(client):
    client.post(
        "/usuarios/cadastro",
        json={
            "nome": "Usuario Login",
            "email": "login@exemplo.com",
            "senha": "SenhaSegura123"
        }
    )

    resposta = client.post(
        "/usuarios/login",
        json={
            "email": "login@exemplo.com",
            "senha": "SenhaSegura123"
        }
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert "access_token" in dados
    assert dados["access_token"]
    assert dados["token_type"] == "bearer"


def test_login_usuario_com_senha_incorreta(client):
    client.post(
        "/usuarios/cadastro",
        json={
            "nome": "Usuario Login",
            "email": "senha.errada@exemplo.com",
            "senha": "SenhaSegura123"
        }
    )

    resposta = client.post(
        "/usuarios/login",
        json={
            "email": "senha.errada@exemplo.com",
            "senha": "SenhaIncorreta999"
        }
    )

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "E-mail ou senha incorretos."


def test_login_usuario_com_email_inexistente(client):
    resposta = client.post(
        "/usuarios/login",
        json={
            "email": "nao.existe@exemplo.com",
            "senha": "SenhaSegura123"
        }
    )

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "E-mail ou senha incorretos."


def test_obter_usuario_autenticado_com_token_valido(client):
    cadastro = client.post(
        "/usuarios/cadastro",
        json={
            "nome": "Usuario Autenticado",
            "email": "me@exemplo.com",
            "senha": "SenhaSegura123"
        }
    )
    usuario_id = cadastro.json()["id"]

    login = client.post(
        "/usuarios/login",
        json={
            "email": "me@exemplo.com",
            "senha": "SenhaSegura123"
        }
    )
    token = login.json()["access_token"]

    resposta = client.get(
        "/usuarios/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 200
    assert resposta.json() == {
        "mensagem": "Token válido.",
        "usuario_id": str(usuario_id)
    }


def test_obter_usuario_autenticado_com_token_invalido(client):
    resposta = client.get(
        "/usuarios/me",
        headers={"Authorization": "Bearer token-invalido"}
    )

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "Token inválido ou expirado."


def test_obter_usuario_autenticado_sem_token(client):
    resposta = client.get("/usuarios/me")

    assert resposta.status_code in (401, 403)

