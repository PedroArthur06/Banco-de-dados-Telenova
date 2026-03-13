from contextlib import asynccontextmanager
from fastapi import FastAPI
from prisma import Prisma

prisma = Prisma()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await prisma.connect()
    yield
    await prisma.disconnect()

from src.controller.webhook_controller import router as webhook_router

app = FastAPI(lifespan=lifespan, title="API Banco Telenova")
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {"message": "API Telenova está online!"}
