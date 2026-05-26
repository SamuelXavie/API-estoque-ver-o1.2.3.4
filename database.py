"""
database.py
─────────────────────────────────────────────────────────────
Conexão com PostgreSQL via asyncpg (assíncrono), compatível com FastAPI.

Pool de Conexões:
  Mantém conexões reutilizáveis prontas para uso, evitando o custo
  de abrir uma nova conexão a cada requisição.

Funções exportadas:
  criar_pool()   → inicializa o pool (chamado na startup da API)
  fechar_pool()  → encerra o pool  (chamado no shutdown da API)
  get_pool()     → retorna o pool ativo para uso nas rotas
"""

import asyncpg
import os
import ssl
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

_pool: Optional[asyncpg.Pool] = None


async def criar_pool() -> None:
    global _pool

    try:
        _pool = await asyncpg.create_pool(
            dsn=os.getenv("DATABASE_URL"),
            min_size=1,
            max_size=5,
            ssl=False,
        )
        print("✅ Pool de conexões criado com sucesso!")
    except Exception as e:
        print(f"⚠️  Aviso ao conectar ao banco: {e}")
        print("    A API está rodando, mas sem conexão com banco de dados.")


async def fechar_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        print("Pool de conexões encerrado.")


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Pool não inicializado. Verifique o startup da aplicação.")
    return _pool
