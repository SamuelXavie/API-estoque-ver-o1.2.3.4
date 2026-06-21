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
        # Detecta se deve usar SSL: variável DATABASE_SSL (true/false) ou
        # ativa por padrão quando a URL aparenta ser do Supabase.
        database_url = os.getenv("DATABASE_URL")
        database_ssl_env = os.getenv("DATABASE_SSL", "auto").lower()

        if database_ssl_env in ("1", "true", "yes"):
            ssl_ctx = ssl.create_default_context()
        elif database_ssl_env == "auto" and database_url and "supabase.co" in database_url:
            ssl_ctx = ssl.create_default_context()
        else:
            ssl_ctx = False

        # Permite desabilitar a verificação de certificado via env (apenas para testes).
        if ssl_ctx and os.getenv("DATABASE_SSL_NO_VERIFY", "false").lower() in ("1", "true", "yes"):
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE

        _pool = await asyncpg.create_pool(
            dsn=database_url,
            min_size=1,
            max_size=5,
            ssl=ssl_ctx,
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
