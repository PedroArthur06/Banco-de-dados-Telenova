from typing import Optional, List, Dict, Any
from prisma import Prisma

class WebhookService:
    def __init__(self, prisma: Prisma):
        self.prisma = prisma

    async def upsert_contato(self, empresa_id: str, dados: Dict[str, Any]) -> Any:
        cpf = dados.get("cpf")
        cnpj = dados.get("cnpj")

        condicao_busca = None
        if cpf:
            condicao_busca = {"empresa_id_cpf": {"empresa_id": empresa_id, "cpf": cpf}}
        else:
            condicao_busca = {"empresa_id_cnpj": {"empresa_id": empresa_id, "cnpj": cnpj}}

        # Busca por (empresa_id + cpf/cnpj). Se achar, atualiza. Se não achar, cria.
        contato_salvo = await self.prisma.cliente_telenova.upsert(
            where=condicao_busca,
            data={
                "create": {
                    "empresa_id": empresa_id,
                    "cpf": cpf,
                    "cnpj": cnpj,
                    "primeiroNome": dados.get("primeiroNome"),
                    "telefone": dados.get("telefone")
                },
                "update": {
                    "primeiroNome": dados.get("primeiroNome"),
                    "telefone": dados.get("telefone")
                }
            }
        )
        return contato_salvo
