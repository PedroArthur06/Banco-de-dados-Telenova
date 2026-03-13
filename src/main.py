from contextlib import asynccontextmanager
from fastapi import FastAPI
from prisma import Prisma

# 1. Instância Global do Prisma
prisma = Prisma()

# 2. Configurando o ciclo de vida da aplicação (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Conecta ao banco de dados ao iniciar
    await prisma.connect()
    yield
    # Desconecta ao desligar
    await prisma.disconnect()

# 3. Importar a rota APIRouter DEPOIS de inicializar o `prisma` acima
# para evitar problemas de importação circular.
from src.controller.webhook_controller import router as webhook_router

# 4. Inicializa o FastAPI
app = FastAPI(lifespan=lifespan, title="API Banco Telenova")

# Adiciona o roteador do webhook com as rotas que configuramos
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {"message": "API Telenova está online!"}
