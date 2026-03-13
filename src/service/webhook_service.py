from typing import Optional, List, Dict, Any
from prisma import Prisma

class WebhookService:
    def __init__(self, prisma: Prisma):
        self.prisma = prisma

    async def upsert_contato(self, dados: Dict[str, Any]) -> Any:

        cliente_id = dados.get("cliente_id")
        cpf = dados.get("cpf")
        cnpj = dados.get("cnpj")

        telefones_prisma = []
        if dados.get("telefones"):
            telefones_prisma = [
                {"telefone": tel["telefone"], "chave": tel.get("chave", False)} 
                for tel in dados["telefones"]
            ]

        condicao_busca = None
        if cpf:
            condicao_busca = {"cliente_id_cpf": {"cliente_id": cliente_id, "cpf": cpf}}
        else:
            condicao_busca = {"cliente_id_cnpj": {"cliente_id": cliente_id, "cnpj": cnpj}}

        # Upsert: Busca. Se achar, atualiza. Se não achar, cria.
        contato_salvo = await self.prisma.contato.upsert(
            where=condicao_busca,
            data={
                "create": {
                    "cliente_id": cliente_id,
                    "cpf": cpf,
                    "cnpj": cnpj,
                    "primeiroNome": dados.get("primeiroNome"),
                    "sobrenome": dados.get("sobrenome"),
                    "rg": dados.get("rg"),
                    "razaoSocial": dados.get("razaoSocial"),
                    "email1": dados.get("email1"),
                    "descricao": dados.get("descricao"),
                    "telefones": {
                        "create": telefones_prisma
                    }
                },
                "update": {
                    "primeiroNome": dados.get("primeiroNome"),
                    "sobrenome": dados.get("sobrenome"),
                    "razaoSocial": dados.get("razaoSocial"),
                    "email1": dados.get("email1"),
                    "descricao": dados.get("descricao"),
                    # Substitui todos os telefones antigos pelos novos enviados
                    "telefones": {
                        "deleteMany": {},
                        "create": telefones_prisma
                    }
                }
            },
            include={
                "telefones": True
            }
        )
        return contato_salvo

    async def listar_contatos(self) -> List[Any]:
        return await self.prisma.contato.find_many(include={"telefones": True})
