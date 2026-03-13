from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Optional
from src.service.webhook_service import WebhookService

try:
    from src.main import prisma
except ImportError:
    from prisma import Prisma
    prisma = Prisma()

router = APIRouter(prefix="/webhook", tags=["Webhook"])
webhook_service = WebhookService(prisma)

class ContatoWebhook(BaseModel):
  
    primeiroNome: str 
    telefone: str 
    cpf: Optional[str] = None
    cnpj: Optional[str] = None


@router.post("/contato")
async def receber_contato(
    dados: ContatoWebhook, 
    x_empresa_id: str = Header(..., description="ID da empresa vindo do n8n")
):
    if not dados.cpf and not dados.cnpj:
        raise HTTPException(
            status_code=400, 
            detail="É obrigatório enviar CPF ou CNPJ para identificar o contato."
        )

    try:
        dados_dict = dados.model_dump()
        
        # Passamos o empresa_id (ID da tabela) para o Service fazer a mágica
        contato_salvo = await webhook_service.upsert_contato(
            empresa_id=x_empresa_id, 
            dados=dados_dict
        )
        
        return {
            "status": "sucesso", 
            "mensagem": f"Contato salvo com sucesso na tabela da Empresa {x_empresa_id}",
            "dados": contato_salvo
        }
    except ValueError as val_err:
        # Se mandar uma empresa que não existe no Prisma
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao salvar no banco.")
