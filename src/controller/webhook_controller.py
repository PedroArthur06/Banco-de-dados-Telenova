from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from src.service.webhook_service import WebhookService
from prisma import Prisma

# Evitamos instanciar o prisma globalmente aqui, usaremos dependência ou receberemos do main
# Porém para manter simples usaremos uma instância para o roteador. Em produção, você pode usar FastAPI Depends.
try:
    # Ajuste de import provisório, vamos importar a instância do prisma do main mais tarde, ou usar dependência
    from src.main import prisma
except ImportError:
    # Fallback
    prisma = Prisma()

router = APIRouter(prefix="/webhook", tags=["Webhook"])
webhook_service = WebhookService(prisma)

class TelefoneInput(BaseModel):
    telefone: str
    chave: bool = False

class ContatoWebhook(BaseModel):
    cliente_id: str
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    primeiroNome: Optional[str] = None
    sobrenome: Optional[str] = None
    rg: Optional[str] = None
    razaoSocial: Optional[str] = None
    email1: Optional[str] = None
    descricao: Optional[str] = None
    telefones: Optional[List[TelefoneInput]] = []

@router.post("/contato")
async def receber_contato(dados: ContatoWebhook):
    # Validação estrutural básica: CPF ou CNPJ são obrigatórios
    if not dados.cpf and not dados.cnpj:
        raise HTTPException(
            status_code=400, 
            detail="É obrigatório enviar CPF ou CNPJ para identificar o contato."
        )

    try:
        # Converter os dados do Pydantic para dict
        dados_dict = dados.model_dump()
        contato_salvo = await webhook_service.upsert_contato(dados_dict)
        
        return {
            "status": "sucesso", 
            "mensagem": "Contato salvo/atualizado com sucesso",
            "dados": contato_salvo
        }
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao salvar no banco.")

@router.get("/contatos")
async def listar_contatos():
    return await webhook_service.listar_contatos()
