import asyncio
import httpx
import time
import uuid

# Configurações do teste
URL = "http://localhost:8000/webhook/contato"
CLIENTES_SIMULTANEOS = 17 
REQUISICOES_POR_CLIENTE = 1000

async def cliente_trabalhador(client, id_cliente):
    resultados = []
    
    # Cada cliente vai preparar 1000 requisições
    headers = {
        "Empresa-Id": f"empresa_teste_{id_cliente}",
        "Content-Type": "application/json"
    }
    
    # Função interna para fazer a requisição de fato
    async def disparar_req(i):
        payload = {
            "primeiroNome": f"Cliente {id_cliente} - Usuario {i}",
            "telefone": f"1198765{i:04d}",
            "cpf": f"{uuid.uuid4().hex[:11]}"
        }
        inicio = time.time()
        try:
            response = await client.post(URL, json=payload, headers=headers)
            return response.status_code, time.time() - inicio
        except Exception as e:
            return "Erro", time.time() - inicio

    # Dispara todas as 1000 deste cliente de uma vez, mas com httpx gerenciando
    tarefas = [disparar_req(x) for x in range(REQUISICOES_POR_CLIENTE)]
    # Usando gather, todas as 1000 saem "simultaneamente" na rede, limitadas pelos slots do OS
    return await asyncio.gather(*tarefas)

async def main():
    total_reqs = CLIENTES_SIMULTANEOS * REQUISICOES_POR_CLIENTE
    print(f"🚀 Iniciando teste extremo...")
    print(f"🎯 Alvo: {URL}")
    print(f"👥 Total de Clientes: {CLIENTES_SIMULTANEOS}")
    print(f"📦 Req/Cliente: {REQUISICOES_POR_CLIENTE}")
    print(f"💣 Total de disparos simultâneos: {total_reqs}\n")
    
    inicio_geral = time.time()
    
    # Usando limits para não estourar o limite de sockets do sistema operacional
    limits = httpx.Limits(max_connections=2000, max_keepalive_connections=2000)
    
    async with httpx.AsyncClient(timeout=60.0, limits=limits) as client:
        # Prepara os 17 clientes para agirem ao mesmo tempo
        clientes = [cliente_trabalhador(client, i) for i in range(1, CLIENTES_SIMULTANEOS + 1)]
        
        # Inicia os 17 clientes simultaneamente
        resultados_clientes = await asyncio.gather(*clientes)
    
    tempo_total = time.time() - inicio_geral
    
    # Analisando resultados
    status_codes = {}
    tempos = []
    
    for resultados_do_cliente in resultados_clientes:
        for status, tempo in resultados_do_cliente:
            status_codes[status] = status_codes.get(status, 0) + 1
            tempos.append(tempo)
    
    print("-" * 30)
    print("📊 RESULTADOS DO TESTE EXTREMO")
    print("-" * 30)
    print(f"⏱️ Tempo Total: {tempo_total:.2f} segundos")
    print(f"🚀 Requisições por segundo (RPS): {total_reqs / tempo_total:.2f}")
    print(f"⏳ Tempo médio por req: {sum(tempos) / len(tempos):.4f} segundos")
    print("\n📈 Retornos da API:")
    for status, count in status_codes.items():
        print(f"   Status {status}: {count} vezes")

if __name__ == "__main__":
    asyncio.run(main())
