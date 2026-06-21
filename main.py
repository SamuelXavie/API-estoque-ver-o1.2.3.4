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

from enum import Enum
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
import uuid

from supabase_client import criar_supabase, fechar_supabase, get_supabase
from starlette.concurrency import run_in_threadpool
from schemas import (
    EstoqueCriar, EstoqueAtualizar, EstoqueResposta,
    LocalFisicoCriar, LocalFisicoAtualizar, LocalFisicoResposta,
    MovimentacaoCriar, MovimentacaoAtualizar, MovimentacaoResposta,
    MovimentacaoTipo,
)


def _normalize_payload(payload: dict) -> dict:
    for k, v in list(payload.items()):
        if isinstance(v, uuid.UUID):
            payload[k] = str(v)
        elif isinstance(v, Enum):
            payload[k] = v.value
    return payload


def _unwrap(res):
    """Normalize Supabase response (object or dict) to {'data', 'error'}."""
    if res is None:
        return {'data': None, 'error': 'no response'}
    if isinstance(res, dict):
        return {'data': res.get('data'), 'error': res.get('error')}
    return {'data': getattr(res, 'data', None), 'error': getattr(res, 'error', None)}


# CORRIGIDO: era síncrona, agora async com run_in_threadpool para não bloquear
# o event loop e retornar resultado correto dentro de rotas async.
async def _exists_in_table(sup, table: str, field: str, value: str) -> bool:
    res = await run_in_threadpool(
        lambda: sup.table(table).select(field).eq(field, value).limit(1).execute()
    )
    u = _unwrap(res)
    if u['error']:
        raise RuntimeError(u['error'])
    return bool(u['data'])


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_in_threadpool(criar_supabase)
    yield
    await run_in_threadpool(fechar_supabase)


app = FastAPI(
    title="API - Módulo de Estoque",
    description="Gerenciamento de estoque, locais físicos e movimentações.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        sup = get_supabase()
        res = await run_in_threadpool(lambda: sup.table('local_fisico').select('id').limit(1).execute())
        u = _unwrap(res)
        if u['error']:
            raise Exception(u['error'])
        return {"status": "ok", "banco": "conectado"}
    except Exception as e:
        return {"status": "erro", "detalhe": str(e)}


# ══════════════════════════════════════════════════════════════
#  LOCAL FÍSICO
# ══════════════════════════════════════════════════════════════

@app.get("/locais", response_model=List[LocalFisicoResposta], tags=["Local Físico"])
async def listar_locais():
    """Lista todos os locais físicos cadastrados."""
    sup = get_supabase()
    res = await run_in_threadpool(lambda: sup.table('local_fisico').select('*').execute())
    u = _unwrap(res)
    if u['error']:
        raise HTTPException(status_code=500, detail=str(u['error']))
    data = u['data'] or []
    data.sort(key=lambda r: r.get('nome') or '')
    return data


@app.get("/locais/{local_id}", response_model=LocalFisicoResposta, tags=["Local Físico"])
async def buscar_local(local_id: uuid.UUID):
    """Retorna um local físico pelo ID."""
    sup = get_supabase()
    res = await run_in_threadpool(lambda: sup.table('local_fisico').select('*').eq('id', str(local_id)).execute())
    u = _unwrap(res)
    if u['error']:
        raise HTTPException(status_code=500, detail=str(u['error']))
    data = u['data'] or []
    if not data:
        raise HTTPException(status_code=404, detail="Local físico não encontrado.")
    return data[0]


@app.post("/locais", response_model=LocalFisicoResposta, status_code=201, tags=["Local Físico"])
async def criar_local(local: LocalFisicoCriar):
    """Cria um novo local físico de armazenamento."""
    sup = get_supabase()
    payload = local.model_dump()
    res = await run_in_threadpool(lambda: sup.table('local_fisico').insert(payload).select('*').execute())
    u = _unwrap(res)
    if u['error']:
        raise HTTPException(status_code=500, detail=str(u['error']))
    return (u['data'] or [None])[0]


@app.put("/locais/{local_id}", response_model=LocalFisicoResposta, tags=["Local Físico"])
async def atualizar_local(local_id: uuid.UUID, local: LocalFisicoAtualizar):
    """Atualiza os dados de um local físico (apenas campos enviados são alterados)."""
    campos = local.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum campo enviado para atualização.")

    sup = get_supabase()
    res = await run_in_threadpool(lambda: sup.table('local_fisico').update(campos).eq('id', str(local_id)).select('*').execute())
    u = _unwrap(res)
    if u['error']:
        raise HTTPException(status_code=500, detail=str(u['error']))
    data = u['data'] or []
    if not data:
        raise HTTPException(status_code=404, detail="Local físico não encontrado.")
    return data[0]


@app.delete("/locais/{local_id}", status_code=200, tags=["Local Físico"])
async def deletar_local(local_id: uuid.UUID):
    """Remove um local físico. Não é possível remover locais com estoque vinculado."""
    sup = get_supabase()
    res = await run_in_threadpool(lambda: sup.table('local_fisico').delete().eq('id', str(local_id)).select('id').execute())
    u = _unwrap(res)
    if u['error']:
        raise HTTPException(status_code=500, detail=str(u['error']))
    data = u['data'] or []
    if not data:
        raise HTTPException(status_code=404, detail="Local físico não encontrado.")
    return {"mensagem": "Local físico excluído com sucesso."}


# ══════════════════════════════════════════════════════════════
#  ESTOQUE
# ORDEM IMPORTA: rotas específicas (/produto/{id}) ANTES de /{id}
# ══════════════════════════════════════════════════════════════

@app.get("/estoques", response_model=List[EstoqueResposta], tags=["Estoque"])
async def listar_estoques():
    """Lista todos os registros de estoque."""
    sup = get_supabase()
    res = await run_in_threadpool(lambda: sup.table('estoque').select('*').execute())
    u = _unwrap(res)
    if u['error']:
        raise HTTPException(status_code=500, detail=str(u['error']))
    data = u['data'] or []
    data.sort(key=lambda r: r.get('created_at') or '', reverse=True)
    return data


# CORRIGIDO: rota específica declarada ANTES de /estoques/{estoque_id}
# para o FastAPI não engolir "produto" como se fosse um UUID.
@app.get("/estoques/produto/{produto_id}", response_model=List[EstoqueResposta], tags=["Estoque"])
async def buscar_estoque_por_produto(produto_id: uuid.UUID):
    """
    Lista todos os registros de estoque de um produto específico
    (pode estar em múltiplos locais físicos).
    """
    sup = get_supabase()
    res = await run_in_threadpool(lambda: sup.table('estoque').select('*').eq('produto_id', str(produto_id)).execute())
    u = _unwrap(res)
    if u['error']:
        raise HTTPException(status_code=500, detail=str(u['error']))
    data = u['data'] or []
    data.sort(key=lambda r: r.get('created_at') or '', reverse=True)
    return data


@app.get("/estoques/{estoque_id}", response_model=EstoqueResposta, tags=["Estoque"])
async def buscar_estoque(estoque_id: uuid.UUID):
    """Retorna um registro de estoque pelo ID."""
    sup = get_supabase()
    res = await run_in_threadpool(lambda: sup.table('estoque').select('*').eq('id', str(estoque_id)).execute())
    u = _unwrap(res)
    if u['error']:
        raise HTTPException(status_code=500, detail=str(u['error']))
    data = u['data'] or []
    if not data:
        raise HTTPException(status_code=404, detail="Registro de estoque não encontrado.")
    return data[0]


@app.post("/estoques", response_model=EstoqueResposta, status_code=201, tags=["Estoque"])
async def criar_estoque(estoque: EstoqueCriar):
    """
    Cria um novo registro de estoque vinculando um produto a um local físico.
    O produto_id deve existir no sistema de Produtos (grupo externo).
    """
    sup = get_supabase()
    payload = _normalize_payload(estoque.model_dump())

    # CORRIGIDO: _exists_in_table agora é async, precisa de await
    if not await _exists_in_table(sup, 'local_fisico', 'id', payload['local_id']):
        raise HTTPException(
            status_code=400,
            detail=f"local_id '{payload['local_id']}' não foi encontrado em local_fisico.",
        )

    res = await run_in_threadpool(lambda: sup.table('estoque').insert(payload).select('*').execute())
    u = _unwrap(res)
    if u['error']:
        message = str(u['error'])
        if 'fk_estoque_local' in message or 'foreign key constraint' in message.lower():
            raise HTTPException(
                status_code=400,
                detail="Erro de integridade referencial: local_id ou produto_id inválido.",
            )
        raise HTTPException(status_code=500, detail=message)
    return (u['data'] or [None])[0]


@app.put("/estoques/{estoque_id}", response_model=EstoqueResposta, tags=["Estoque"])
async def atualizar_estoque(estoque_id: uuid.UUID, estoque: EstoqueAtualizar):
    """Atualiza um registro de estoque (apenas campos enviados são alterados)."""
    campos = estoque.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum campo enviado para atualização.")

    sup = get_supabase()

    # CORRIGIDO: _exists_in_table agora é async, precisa de await
    if 'local_id' in campos and not await _exists_in_table(sup, 'local_fisico', 'id', str(campos['local_id'])):
        raise HTTPException(
            status_code=400,
            detail=f"local_id '{campos['local_id']}' não foi encontrado em local_fisico.",
        )

    payload = _normalize_payload(campos)
    res = await run_in_threadpool(lambda: sup.table('estoque').update(payload).eq('id', str(estoque_id)).select('*').execute())
    u = _unwrap(res)
    if u['error']:
        message = str(u['error'])
        if 'fk_estoque_local' in message or 'foreign key constraint' in message.lower():
            raise HTTPException(
                status_code=400,
                detail="Erro de integridade referencial: local_id ou produto_id inválido.",
            )
        raise HTTPException(status_code=500, detail=message)
    data = u['data'] or []
    if not data:
        raise HTTPException(status_code=404, detail="Registro de estoque não encontrado.")
    return data[0]


@app.delete("/estoques/{estoque_id}", status_code=200, tags=["Estoque"])
async def deletar_estoque(estoque_id: uuid.UUID):
    """Remove um registro de estoque. As movimentações associadas são mantidas como histórico."""
    sup = get_supabase()
    res = await run_in_threadpool(lambda: sup.table('estoque').delete().eq('id', str(estoque_id)).select('id').execute())
    u = _unwrap(res)
    if u['error']:
        raise HTTPException(status_code=500, detail=str(u['error']))
    data = u['data'] or []
    if not data:
        raise HTTPException(status_code=404, detail="Registro de estoque não encontrado.")
    return {"mensagem": "Registro de estoque excluído com sucesso."}


# ══════════════════════════════════════════════════════════════
#  MOVIMENTAÇÃO DE ESTOQUE
# ORDEM IMPORTA: /estoque/{id} ANTES de /{id}
# ══════════════════════════════════════════════════════════════

@app.get("/movimentacoes", response_model=List[MovimentacaoResposta], tags=["Movimentação de Estoque"])
async def listar_movimentacoes():
    """Lista todas as movimentações de estoque, da mais recente para a mais antiga."""
    sup = get_supabase()
    res = await run_in_threadpool(lambda: sup.table('movimentacao_estoque').select('*').execute())
    u = _unwrap(res)
    if u['error']:
        raise HTTPException(status_code=500, detail=str(u['error']))
    data = u['data'] or []
    data.sort(key=lambda r: r.get('created_at') or '', reverse=True)
    return data


# CORRIGIDO: rota específica declarada ANTES de /movimentacoes/{movimentacao_id}
@app.get("/movimentacoes/estoque/{estoque_id}", response_model=List[MovimentacaoResposta], tags=["Movimentação de Estoque"])
async def listar_movimentacoes_por_estoque(estoque_id: uuid.UUID):
    """Lista todas as movimentações de um registro de estoque específico."""
    sup = get_supabase()
    res = await run_in_threadpool(lambda: sup.table('movimentacao_estoque').select('*').eq('estoque_id', str(estoque_id)).execute())
    u = _unwrap(res)
    if u['error']:
        raise HTTPException(status_code=500, detail=str(u['error']))
    data = u['data'] or []
    data.sort(key=lambda r: r.get('created_at') or '', reverse=True)
    return data


@app.get("/movimentacoes/{movimentacao_id}", response_model=MovimentacaoResposta, tags=["Movimentação de Estoque"])
async def buscar_movimentacao(movimentacao_id: uuid.UUID):
    """Retorna uma movimentação específica pelo ID."""
    sup = get_supabase()
    res = await run_in_threadpool(lambda: sup.table('movimentacao_estoque').select('*').eq('id', str(movimentacao_id)).execute())
    u = _unwrap(res)
    if u['error']:
        raise HTTPException(status_code=500, detail=str(u['error']))
    data = u['data'] or []
    if not data:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada.")
    return data[0]


# CORRIGIDO: apenas um decorador — múltiplos @app.post empilhados fazem
# somente o último ficar ativo no FastAPI, os demais são ignorados.
@app.post("/movimentacoes", response_model=MovimentacaoResposta, status_code=201, tags=["Movimentação de Estoque"])
async def criar_movimentacao(mov: MovimentacaoCriar):
    """
    Registra uma movimentação de estoque (entrada ou saída) e atualiza
    automaticamente a quantidade na tabela estoque.

    - tipo 'entrada': soma a quantidade ao estoque
    - tipo 'saida':   subtrai a quantidade do estoque (retorna 400 se insuficiente)
    """
    sup = get_supabase()

    # Busca o estoque atual
    res = await run_in_threadpool(lambda: sup.table('estoque').select('id,quantidade').eq('id', str(mov.estoque_id)).execute())
    u = _unwrap(res)
    if u['error']:
        raise HTTPException(status_code=500, detail=str(u['error']))
    data = u['data'] or []
    if not data:
        raise HTTPException(status_code=404, detail="Registro de estoque não encontrado.")
    estoque_row = data[0]

    # Valida saldo disponível para saídas
    if mov.tipo == MovimentacaoTipo.saida and estoque_row.get('quantidade', 0) < mov.quantidade:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Disponível: {estoque_row.get('quantidade', 0)}, solicitado: {mov.quantidade}.",
        )

    # Calcula nova quantidade
    nova_qtd = (
        estoque_row.get('quantidade', 0) + mov.quantidade
        if mov.tipo == MovimentacaoTipo.entrada
        else estoque_row.get('quantidade', 0) - mov.quantidade
    )

    # Atualiza estoque
    upd = await run_in_threadpool(lambda: sup.table('estoque').update({'quantidade': nova_qtd}).eq('id', str(mov.estoque_id)).select('*').execute())
    u_upd = _unwrap(upd)
    if u_upd['error']:
        raise HTTPException(status_code=500, detail=str(u_upd['error']))

    # Registra a movimentação
    payload = _normalize_payload(mov.model_dump())
    res_ins = await run_in_threadpool(lambda: sup.table('movimentacao_estoque').insert(payload).select('*').execute())
    u_ins = _unwrap(res_ins)
    if u_ins['error']:
        raise HTTPException(status_code=500, detail=str(u_ins['error']))
    return (u_ins['data'] or [None])[0]


@app.put("/movimentacoes/{movimentacao_id}", response_model=MovimentacaoResposta, tags=["Movimentação de Estoque"])
async def atualizar_movimentacao(movimentacao_id: uuid.UUID, mov: MovimentacaoAtualizar):
    """
    Atualiza tipo ou observação de uma movimentação já registrada.
    A quantidade não pode ser alterada aqui; crie uma movimentação corretiva se necessário.
    """
    campos = mov.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum campo enviado para atualização.")

    # CORRIGIDO: campos["tipo"] agora pode ser MovimentacaoTipo (enum), não só string.
    # O check anterior comparava enum com string e sempre falhava.
    if "tipo" in campos:
        tipo_val = campos["tipo"]
        tipo_str = tipo_val.value if isinstance(tipo_val, MovimentacaoTipo) else str(tipo_val)
        if tipo_str not in ("entrada", "saida"):
            raise HTTPException(status_code=400, detail="Tipo deve ser 'entrada' ou 'saida'.")
        campos["tipo"] = tipo_str  # garante que vai para o Supabase como string

    sup = get_supabase()
    res = await run_in_threadpool(lambda: sup.table('movimentacao_estoque').update(campos).eq('id', str(movimentacao_id)).select('*').execute())
    u = _unwrap(res)
    if u['error']:
        raise HTTPException(status_code=500, detail=str(u['error']))
    data = u['data'] or []
    if not data:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada.")
    return data[0]


@app.delete("/movimentacoes/{movimentacao_id}", status_code=200, tags=["Movimentação de Estoque"])
async def deletar_movimentacao(movimentacao_id: uuid.UUID):
    """
    Remove um registro de movimentação do histórico.
    Atenção: não reverte automaticamente o saldo do estoque.
    Use com cuidado — prefira criar uma movimentação corretiva.
    """
    sup = get_supabase()
    res = await run_in_threadpool(lambda: sup.table('movimentacao_estoque').delete().eq('id', str(movimentacao_id)).select('id').execute())
    u = _unwrap(res)
    if u['error']:
        raise HTTPException(status_code=500, detail=str(u['error']))
    data = u['data'] or []
    if not data:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada.")
    return {"mensagem": "Movimentação excluída do histórico com sucesso."}
