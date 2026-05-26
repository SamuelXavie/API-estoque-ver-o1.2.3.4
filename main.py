"""
main.py
=============================================================
  API REST - Módulo de Estoque
  Disciplina: Sistemas Distribuídos - Etapa 3
  Escopo: tabelas estoque, local_fisico, movimentacao_estoque
=============================================================
  Como rodar:
    1. pip install fastapi uvicorn asyncpg python-dotenv
    2. Crie .env com: DATABASE_URL=postgresql://user:senha@host/db
    3. uvicorn main:app --reload
    Documentação automática: http://localhost:8000/docs
=============================================================
"""

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from typing import List
import uuid

from database import criar_pool, fechar_pool, get_pool
# Alterar: DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/estoque_dbl
from schemas import (
    EstoqueCriar, EstoqueAtualizar, EstoqueResposta,
    LocalFisicoCriar, LocalFisicoAtualizar, LocalFisicoResposta,
    MovimentacaoCriar, MovimentacaoAtualizar, MovimentacaoResposta,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await criar_pool()
    yield
    await fechar_pool()


app = FastAPI(
    title="API - Módulo de Estoque",
    description="Gerenciamento de estoque, locais físicos e movimentações.",
    version="2.0.0",
    lifespan=lifespan,
)


# ══════════════════════════════════════════════════════════════
#  ROTAS GERAIS
# ══════════════════════════════════════════════════════════════

@app.get("/", tags=["Geral"])
async def raiz():
    return {"mensagem": "API de Estoque funcionando! Acesse /docs"}


@app.get("/health", tags=["Geral"])
async def health_check():
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "ok", "banco": "conectado"}
    except Exception as e:
        return {"status": "erro", "detalhe": str(e)}


# ══════════════════════════════════════════════════════════════
#  LOCAL FÍSICO
# ══════════════════════════════════════════════════════════════

@app.get("/locais", response_model=List[LocalFisicoResposta], tags=["Local Físico"])
async def listar_locais():
    """Lista todos os locais físicos cadastrados."""
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM local_fisico ORDER BY nome ASC")
    return [dict(r) for r in rows]


@app.get("/locais/{local_id}", response_model=LocalFisicoResposta, tags=["Local Físico"])
async def buscar_local(local_id: uuid.UUID):
    """Retorna um local físico pelo ID."""
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM local_fisico WHERE id = $1", local_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Local físico não encontrado.")
    return dict(row)


@app.post("/locais", response_model=LocalFisicoResposta, status_code=201, tags=["Local Físico"])
async def criar_local(local: LocalFisicoCriar):
    """Cria um novo local físico de armazenamento."""
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO local_fisico (nome, descricao, ativo)
            VALUES ($1, $2, $3)
            RETURNING *
            """,
            local.nome, local.descricao, local.ativo,
        )
    return dict(row)


@app.put("/locais/{local_id}", response_model=LocalFisicoResposta, tags=["Local Físico"])
async def atualizar_local(local_id: uuid.UUID, local: LocalFisicoAtualizar):
    """Atualiza os dados de um local físico (apenas campos enviados são alterados)."""
    campos = local.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum campo enviado para atualização.")

    set_clause = ", ".join(f"{k} = ${i+1}" for i, k in enumerate(campos))
    valores = list(campos.values()) + [local_id]

    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"UPDATE local_fisico SET {set_clause} WHERE id = ${len(valores)} RETURNING *",
            *valores,
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Local físico não encontrado.")
    return dict(row)


@app.delete("/locais/{local_id}", status_code=200, tags=["Local Físico"])
async def deletar_local(local_id: uuid.UUID):
    """Remove um local físico. Não é possível remover locais com estoque vinculado."""
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "DELETE FROM local_fisico WHERE id = $1 RETURNING id", local_id
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Local físico não encontrado.")
    return {"mensagem": "Local físico excluído com sucesso."}


# ══════════════════════════════════════════════════════════════
#  ESTOQUE
# ══════════════════════════════════════════════════════════════

@app.get("/estoques", response_model=List[EstoqueResposta], tags=["Estoque"])
async def listar_estoques():
    """Lista todos os registros de estoque."""
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM estoque ORDER BY created_at DESC")
    return [dict(r) for r in rows]


@app.get("/estoques/{estoque_id}", response_model=EstoqueResposta, tags=["Estoque"])
async def buscar_estoque(estoque_id: uuid.UUID):
    """Retorna um registro de estoque pelo ID."""
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM estoque WHERE id = $1", estoque_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Registro de estoque não encontrado.")
    return dict(row)


@app.get("/estoques/produto/{produto_id}", response_model=List[EstoqueResposta], tags=["Estoque"])
async def buscar_estoque_por_produto(produto_id: uuid.UUID):
    """
    Lista todos os registros de estoque de um produto específico
    (pode estar em múltiplos locais físicos).
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM estoque WHERE produto_id = $1 ORDER BY created_at DESC",
            produto_id,
        )
    return [dict(r) for r in rows]


@app.post("/estoques", response_model=EstoqueResposta, status_code=201, tags=["Estoque"])
async def criar_estoque(estoque: EstoqueCriar):
    """
    Cria um novo registro de estoque vinculando um produto a um local físico.
    O produto_id deve existir no sistema de Produtos (grupo externo).
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO estoque (produto_id, local_id, quantidade, quantidade_minima, quantidade_maxima)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
            """,
            estoque.produto_id, estoque.local_id, estoque.quantidade,
            estoque.quantidade_minima, estoque.quantidade_maxima,
        )
    return dict(row)


@app.put("/estoques/{estoque_id}", response_model=EstoqueResposta, tags=["Estoque"])
async def atualizar_estoque(estoque_id: uuid.UUID, estoque: EstoqueAtualizar):
    """Atualiza um registro de estoque (apenas campos enviados são alterados)."""
    campos = estoque.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum campo enviado para atualização.")

    set_clause = ", ".join(f"{k} = ${i+1}" for i, k in enumerate(campos))
    valores = list(campos.values()) + [estoque_id]

    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"UPDATE estoque SET {set_clause} WHERE id = ${len(valores)} RETURNING *",
            *valores,
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Registro de estoque não encontrado.")
    return dict(row)


@app.delete("/estoques/{estoque_id}", status_code=200, tags=["Estoque"])
async def deletar_estoque(estoque_id: uuid.UUID):
    """Remove um registro de estoque. As movimentações associadas são mantidas como histórico."""
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "DELETE FROM estoque WHERE id = $1 RETURNING id", estoque_id
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Registro de estoque não encontrado.")
    return {"mensagem": "Registro de estoque excluído com sucesso."}


# ══════════════════════════════════════════════════════════════
#  MOVIMENTAÇÃO DE ESTOQUE
# ══════════════════════════════════════════════════════════════

@app.get("/movimentacoes", response_model=List[MovimentacaoResposta], tags=["Movimentação de Estoque"])
async def listar_movimentacoes():
    """Lista todas as movimentações de estoque, da mais recente para a mais antiga."""
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM movimentacao_estoque ORDER BY created_at DESC")
    return [dict(r) for r in rows]


@app.get("/movimentacoes/{movimentacao_id}", response_model=MovimentacaoResposta, tags=["Movimentação de Estoque"])
async def buscar_movimentacao(movimentacao_id: uuid.UUID):
    """Retorna uma movimentação específica pelo ID."""
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM movimentacao_estoque WHERE id = $1", movimentacao_id
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada.")
    return dict(row)


@app.get("/movimentacoes/estoque/{estoque_id}", response_model=List[MovimentacaoResposta], tags=["Movimentação de Estoque"])
async def listar_movimentacoes_por_estoque(estoque_id: uuid.UUID):
    """Lista todas as movimentações de um registro de estoque específico."""
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM movimentacao_estoque WHERE estoque_id = $1 ORDER BY created_at DESC",
            estoque_id,
        )
    return [dict(r) for r in rows]


@app.post("/movimentacoes", response_model=MovimentacaoResposta, status_code=201, tags=["Movimentação de Estoque"])
async def criar_movimentacao(mov: MovimentacaoCriar):
    """
    Registra uma movimentação de estoque (entrada ou saída) e atualiza
    automaticamente a quantidade na tabela estoque.

    - tipo 'entrada': soma a quantidade ao estoque
    - tipo 'saida':   subtrai a quantidade do estoque (retorna 400 se insuficiente)
    """
    if mov.tipo not in ("entrada", "saida"):
        raise HTTPException(status_code=400, detail="Tipo deve ser 'entrada' ou 'saida'.")

    pool = get_pool()
    async with pool.acquire() as conn:

        # Verifica se o estoque existe e busca a quantidade atual
        estoque_row = await conn.fetchrow(
            "SELECT id, quantidade FROM estoque WHERE id = $1", mov.estoque_id
        )
        if estoque_row is None:
            raise HTTPException(status_code=404, detail="Registro de estoque não encontrado.")

        # Valida saldo disponível para saídas
        if mov.tipo == "saida" and estoque_row["quantidade"] < mov.quantidade:
            raise HTTPException(
                status_code=400,
                detail=f"Saldo insuficiente. Disponível: {estoque_row['quantidade']}, solicitado: {mov.quantidade}.",
            )

        # Calcula nova quantidade
        nova_qtd = (
            estoque_row["quantidade"] + mov.quantidade
            if mov.tipo == "entrada"
            else estoque_row["quantidade"] - mov.quantidade
        )

        # Atualiza estoque e registra movimentação em uma transação
        async with conn.transaction():
            await conn.execute(
                "UPDATE estoque SET quantidade = $1 WHERE id = $2",
                nova_qtd, mov.estoque_id,
            )
            row = await conn.fetchrow(
                """
                INSERT INTO movimentacao_estoque (estoque_id, tipo, quantidade, observacao)
                VALUES ($1, $2, $3, $4)
                RETURNING *
                """,
                mov.estoque_id, mov.tipo, mov.quantidade, mov.observacao,
            )

    return dict(row)


@app.put("/movimentacoes/{movimentacao_id}", response_model=MovimentacaoResposta, tags=["Movimentação de Estoque"])
async def atualizar_movimentacao(movimentacao_id: uuid.UUID, mov: MovimentacaoAtualizar):
    """
    Atualiza tipo ou observação de uma movimentação já registrada.
    A quantidade não pode ser alterada aqui; crie uma movimentação corretiva se necessário.
    """
    campos = mov.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum campo enviado para atualização.")

    if "tipo" in campos and campos["tipo"] not in ("entrada", "saida"):
        raise HTTPException(status_code=400, detail="Tipo deve ser 'entrada' ou 'saida'.")

    set_clause = ", ".join(f"{k} = ${i+1}" for i, k in enumerate(campos))
    valores = list(campos.values()) + [movimentacao_id]

    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"UPDATE movimentacao_estoque SET {set_clause} WHERE id = ${len(valores)} RETURNING *",
            *valores,
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada.")
    return dict(row)


@app.delete("/movimentacoes/{movimentacao_id}", status_code=200, tags=["Movimentação de Estoque"])
async def deletar_movimentacao(movimentacao_id: uuid.UUID):
    """
    Remove um registro de movimentação do histórico.
    Atenção: não reverte automaticamente o saldo do estoque.
    Use com cuidado — prefira criar uma movimentação corretiva.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "DELETE FROM movimentacao_estoque WHERE id = $1 RETURNING id", movimentacao_id
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada.")
    return {"mensagem": "Movimentação excluída do histórico com sucesso."}
