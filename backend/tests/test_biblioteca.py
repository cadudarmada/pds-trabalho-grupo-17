def _criar_usuario_e_obter_headers(client, nome: str, email: str) -> dict:
    client.post(
        "/usuarios/cadastro",
        json={
            "nome": nome,
            "email": email,
            "senha": "SenhaSegura123",
        },
    )

    login = client.post(
        "/usuarios/login",
        json={
            "email": email,
            "senha": "SenhaSegura123",
        },
    )

    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _payload_livro(google_books_id: str = "gb_vento", titulo: str = "O Nome do Vento") -> dict:
    return {
        "google_books_id": google_books_id,
        "titulo": titulo,
        "autores": ["Patrick Rothfuss"],
        "editora": "Arqueiro",
        "data_publicacao": "2009",
        "isbn": "9788599296493",
        "descricao": "A história de Kvothe.",
        "capa": "https://exemplo.com/capa.jpg",
    }


def test_biblioteca_exige_autenticacao(client):
    resposta_post = client.post("/biblioteca", json=_payload_livro())
    resposta_get = client.get("/biblioteca")

    assert resposta_post.status_code in (401, 403)
    assert resposta_get.status_code in (401, 403)


def test_listar_biblioteca_vazia(client):
    headers = _criar_usuario_e_obter_headers(client, "Ana Silva", "ana@exemplo.com")

    resposta = client.get("/biblioteca", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_adicionar_e_listar_livro_na_biblioteca(client):
    headers = _criar_usuario_e_obter_headers(client, "Ana Silva", "ana@exemplo.com")

    resposta_post = client.post(
        "/biblioteca",
        json=_payload_livro(),
        headers=headers,
    )

    assert resposta_post.status_code == 201
    item = resposta_post.json()
    assert item["id"] > 0
    assert "data_adicao" in item
    assert item["livro"]["google_books_id"] == "gb_vento"
    assert item["livro"]["titulo"] == "O Nome do Vento"
    assert item["livro"]["autores"] == ["Patrick Rothfuss"]

    resposta_get = client.get("/biblioteca", headers=headers)

    assert resposta_get.status_code == 200
    lista = resposta_get.json()
    assert len(lista) == 1
    assert lista[0]["livro"]["titulo"] == "O Nome do Vento"


def test_adicionar_livro_duplicado_retorna_409(client):
    headers = _criar_usuario_e_obter_headers(client, "Ana Silva", "ana@exemplo.com")
    payload = _payload_livro()

    primeira = client.post("/biblioteca", json=payload, headers=headers)
    segunda = client.post("/biblioteca", json=payload, headers=headers)

    assert primeira.status_code == 201
    assert segunda.status_code == 409
    assert segunda.json()["detail"] == "Este livro já está na sua biblioteca."


def test_usuarios_diferentes_podem_adicionar_mesmo_livro_com_bibliotecas_isoladas(client):
    headers_ana = _criar_usuario_e_obter_headers(client, "Ana Silva", "ana@exemplo.com")
    headers_bruno = _criar_usuario_e_obter_headers(client, "Bruno Lima", "bruno@exemplo.com")

    resp_ana = client.post(
        "/biblioteca",
        json=_payload_livro("gb_duna", "Duna"),
        headers=headers_ana,
    )
    resp_bruno = client.post(
        "/biblioteca",
        json=_payload_livro("gb_duna", "Duna"),
        headers=headers_bruno,
    )
    client.post(
        "/biblioteca",
        json=_payload_livro("gb_fundacao", "Fundação"),
        headers=headers_ana,
    )

    assert resp_ana.status_code == 201
    assert resp_bruno.status_code == 201
    assert resp_ana.json()["livro"]["id"] == resp_bruno.json()["livro"]["id"]

    lista_ana = client.get("/biblioteca", headers=headers_ana).json()
    lista_bruno = client.get("/biblioteca", headers=headers_bruno).json()

    assert [item["livro"]["titulo"] for item in lista_ana] == ["Fundação", "Duna"]
    assert [item["livro"]["titulo"] for item in lista_bruno] == ["Duna"]


def test_livro_adicionado_inicia_com_status_quero_ler(client):
    headers = _criar_usuario_e_obter_headers(client, "Ana Silva", "ana@exemplo.com")

    resposta = client.post("/biblioteca", json=_payload_livro(), headers=headers)

    assert resposta.status_code == 201
    assert resposta.json()["status"] == "QUERO_LER"


def test_atualizar_status_leitura_com_sucesso(client):
    headers = _criar_usuario_e_obter_headers(client, "Ana Silva", "ana@exemplo.com")

    criado = client.post("/biblioteca", json=_payload_livro(), headers=headers).json()
    item_id = criado["id"]

    for novo_status in ("LENDO", "LIDO", "ABANDONADO"):
        resposta = client.patch(
            f"/biblioteca/{item_id}/status",
            json={"status": novo_status},
            headers=headers,
        )

        assert resposta.status_code == 200
        assert resposta.json()["status"] == novo_status

    lista = client.get("/biblioteca", headers=headers).json()
    assert lista[0]["status"] == "ABANDONADO"


def test_atualizar_status_com_valor_invalido_retorna_422(client):
    headers = _criar_usuario_e_obter_headers(client, "Ana Silva", "ana@exemplo.com")
    criado = client.post("/biblioteca", json=_payload_livro(), headers=headers).json()

    resposta = client.patch(
        f"/biblioteca/{criado['id']}/status",
        json={"status": "CONCLUIDO"},
        headers=headers,
    )

    assert resposta.status_code == 422


def test_atualizar_status_sem_autenticacao(client):
    resposta = client.patch("/biblioteca/1/status", json={"status": "LENDO"})

    assert resposta.status_code in (401, 403)


def test_atualizar_status_item_inexistente_retorna_404(client):
    headers = _criar_usuario_e_obter_headers(client, "Ana Silva", "ana@exemplo.com")

    resposta = client.patch(
        "/biblioteca/999/status",
        json={"status": "LIDO"},
        headers=headers,
    )

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Livro não encontrado na sua biblioteca."


def test_usuario_nao_pode_atualizar_status_de_livro_de_outro_usuario(client):
    headers_ana = _criar_usuario_e_obter_headers(client, "Ana Silva", "ana@exemplo.com")
    headers_bruno = _criar_usuario_e_obter_headers(client, "Bruno Lima", "bruno@exemplo.com")

    item_ana = client.post("/biblioteca", json=_payload_livro(), headers=headers_ana).json()

    tentativa_bruno = client.patch(
        f"/biblioteca/{item_ana['id']}/status",
        json={"status": "LIDO"},
        headers=headers_bruno,
    )

    assert tentativa_bruno.status_code == 404

    biblioteca_ana = client.get("/biblioteca", headers=headers_ana).json()
    assert biblioteca_ana[0]["status"] == "QUERO_LER"


def test_filtrar_biblioteca_por_status(client):
    headers = _criar_usuario_e_obter_headers(client, "Ana Silva", "ana@exemplo.com")

    item_duna = client.post(
        "/biblioteca", json=_payload_livro("gb_1", "Duna"), headers=headers
    ).json()
    item_fundacao = client.post(
        "/biblioteca", json=_payload_livro("gb_2", "Fundação"), headers=headers
    ).json()
    client.post(
        "/biblioteca", json=_payload_livro("gb_3", "O Hobbit"), headers=headers
    )

    client.patch(
        f"/biblioteca/{item_duna['id']}/status",
        json={"status": "LENDO"},
        headers=headers,
    )
    client.patch(
        f"/biblioteca/{item_fundacao['id']}/status",
        json={"status": "LIDO"},
        headers=headers,
    )

    lendo = client.get("/biblioteca", params={"status": "LENDO"}, headers=headers)
    lido = client.get("/biblioteca", params={"status": "LIDO"}, headers=headers)
    abandonado = client.get(
        "/biblioteca", params={"status": "ABANDONADO"}, headers=headers
    )
    invalido = client.get(
        "/biblioteca", params={"status": "INVALIDO"}, headers=headers
    )

    assert lendo.status_code == 200
    assert [item["livro"]["titulo"] for item in lendo.json()] == ["Duna"]

    assert lido.status_code == 200
    assert [item["livro"]["titulo"] for item in lido.json()] == ["Fundação"]

    assert abandonado.status_code == 200
    assert abandonado.json() == []

    assert invalido.status_code == 422
