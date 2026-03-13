import pytest
from fastapi.testclient import TestClient
from src.main import app

def test_criar_contato_sucesso():
    payload = {
        "primeiroNome": "Pedro Arthur",
        "telefone": "65996326845",
        "cpf": "09334956178"
    }

    headers = {
        "Empresa-Id": "10"
    }

    with TestClient(app) as client:
        response = client.post("/webhook/contato", json=payload, headers=headers)

    assert response.status_code == 200
    dados_resposta = response.json()
    assert dados_resposta["status"] == "sucesso"
    
    contato_banco = dados_resposta["dados"]
    assert contato_banco["primeiroNome"] == "Pedro Arthur"
    assert contato_banco["telefone"] == "65996326845"
    assert contato_banco["cpf"] == "09334956178"
    assert contato_banco["empresa_id"] == "10"

def test_atualizar_contato_existente():
    payload_atualizado = {
        "primeiroNome": "Pedro Arthur Atualizado",
        "telefone": "65996326845",
        "cpf": "09334956178"
    }

    headers = {
        "Empresa-Id": "10"
    }

    with TestClient(app) as client:
        response = client.post("/webhook/contato", json=payload_atualizado, headers=headers)

    assert response.status_code == 200
    dados_resposta = response.json()
    
    contato_banco = dados_resposta["dados"]
    assert contato_banco["primeiroNome"] == "Pedro Arthur Atualizado"
    assert contato_banco["telefone"] == "65996326845"

def test_falha_sem_cpf_e_cnpj():
    payload_invalido = {
        "primeiroNome": "Jacó",
        "telefone": "65996326845"
    }

    headers = {
        "Empresa-Id": "20"
    }

    with TestClient(app) as client:
        response = client.post("/webhook/contato", json=payload_invalido, headers=headers)

    assert response.status_code == 400
    assert "obrigatório" in response.json()["detail"].lower() or "obrigatório" in response.json()["detail"]

def test_falha_sem_primeiro_nome():
    payload_invalido = {
        "telefone": "11988888888",
        "cpf": "11122233344"
    }

    headers = {
        "Empresa-Id": "20"
    }

    with TestClient(app) as client:
        response = client.post("/webhook/contato", json=payload_invalido, headers=headers)

    assert response.status_code == 422
    detalhes_erro = response.json()["detail"]
    assert detalhes_erro[0]["loc"] == ["body", "primeiroNome"]
