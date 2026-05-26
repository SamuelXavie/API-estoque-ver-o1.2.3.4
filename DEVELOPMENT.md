# 🛠️ Guia de Desenvolvimento

## Bem-vindo ao desenvolvimento da API de Estoque!

Este guia descreve como contribuir e estender a API.

---

## 📁 Estrutura dos Arquivos

```
estoque_api/
├── main.py              # Rotas e endpoints
├── database.py          # Configuração de banco
├── schemas.py           # Modelos Pydantic
├── requirements.txt     # Dependências
├── .env.example         # Template de env
├── .env                 # Variáveis (não commitar!)
├── venv/                # Ambiente virtual
├── README.md            # Documentação principal
├── API_REFERENCE.md     # Referência de endpoints
├── COMO_RODAR.md        # Guia de setup
├── QUICK_START.md       # Início rápido
└── DEVELOPMENT.md       # Este arquivo
```

---

## 🚀 Setup de Desenvolvimento

### 1. Clonar e Configurar

```bash
cd estoque\ atualizado
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar Banco

```bash
cp .env.example .env
# Editar .env com suas credenciais

createdb estoque_db
```

### 3. Rodar em Modo Desenvolvimento

```bash
uvicorn main:app --reload
```

**O `--reload` reinicia a API quando há mudanças nos arquivos**

---

## 📝 Adicionando um Novo Endpoint

### Exemplo: Adicionar endpoint de busca por nome de local

#### 1. Adicione a rota no `main.py`

```python
@app.get("/locais/nome/{nome}", response_model=List[LocalFisicoResposta], tags=["Local Físico"])
async def buscar_locais_por_nome(nome: str):
    """Busca locais físicos por nome (case-insensitive)."""
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM local_fisico WHERE LOWER(nome) LIKE LOWER($1) ORDER BY nome ASC",
            f"%{nome}%"
        )
    return [dict(r) for r in rows]
```

#### 2. Use a API

```bash
curl http://localhost:8000/locais/nome/prateleira
```

---

## 🧪 Testando Endpoints

### Usando cURL

```bash
# GET
curl http://localhost:8000/locais

# POST
curl -X POST http://localhost:8000/locais \
  -H "Content-Type: application/json" \
  -d '{"nome": "Novo Local", "ativo": true}'

# PUT
curl -X PUT http://localhost:8000/locais/ID \
  -H "Content-Type: application/json" \
  -d '{"nome": "Local Atualizado"}'

# DELETE
curl -X DELETE http://localhost:8000/locais/ID
```

### Usando Swagger UI

Acesse **http://localhost:8000/docs** e teste diretamente na interface!

---

## 🔄 Fluxo de Movimentação

```
┌─────────────────────────────┐
│  Cliente faz requisição POST │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  main.py valida dados       │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  database.py obtém conexão  │
│  do pool                    │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Executa query no PostgreSQL │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Retorna resultado como dict │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Valida com Pydantic schema │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Retorna JSON ao cliente    │
└─────────────────────────────┘
```

---

## 📚 Entendendo os Modelos

### schemas.py - Modelos Pydantic

```python
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

# ✅ Modelo para criar
class LocalFisicoCriar(BaseModel):
    nome: str = Field(..., max_length=100)
    descricao: Optional[str] = None
    ativo: bool = Field(True)

# ✅ Modelo para atualizar (todos opcionais)
class LocalFisicoAtualizar(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None

# ✅ Modelo para resposta
class LocalFisicoResposta(BaseModel):
    id: uuid.UUID
    nome: str
    descricao: Optional[str]
    ativo: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Converte Dict para objeto
```

---

## 🗄️ Database Pool

### Como Funciona

```python
# database.py cria um pool durante a startup
async def criar_pool():
    _pool = await asyncpg.create_pool(
        dsn=os.getenv("DATABASE_URL"),
        min_size=1,   # Mínimo de conexões
        max_size=5,   # Máximo de conexões
    )

# Cada rota reutiliza conexões do pool
@app.get("/locais")
async def listar_locais():
    pool = get_pool()
    async with pool.acquire() as conn:
        # Usa a conexão
        rows = await conn.fetch("SELECT * FROM local_fisico")
    # Conexão retorna ao pool automaticamente
    return rows
```

### Por que usar Pool?

- ✅ **Performance**: Reutiliza conexões
- ✅ **Escalabilidade**: Suporta múltiplas requisições
- ✅ **Segurança**: Gerencia recursos automaticamente

---

## 🔐 Validações Importantes

### Modelos Pydantic automaticamente validam:

```python
# Exemplo: EstoqueCriar
class EstoqueCriar(BaseModel):
    produto_id: uuid.UUID              # Valida se é UUID
    local_id: uuid.UUID                # Valida se é UUID
    quantidade: int = Field(..., ge=0) # >= 0
    quantidade_minima: Optional[int] = Field(0, ge=0)
    quantidade_maxima: Optional[int] = Field(None, ge=0)
```

**Se enviar dados inválidos:**
```bash
curl -X POST http://localhost:8000/estoques \
  -d '{"produto_id": "invalid", "quantidade": -10}'

# Response 422:
{
  "detail": [
    {"loc": ["body", "produto_id"], "msg": "invalid uuid format"},
    {"loc": ["body", "quantidade"], "msg": "ensure this value is greater than or equal to 0"}
  ]
}
```

---

## 💾 Adicionando Lógica de Negócio

### Exemplo: Atualizar automática de quantidade

```python
@app.post("/movimentacoes", response_model=MovimentacaoResposta)
async def criar_movimentacao(mov: MovimentacaoCriar):
    if mov.tipo not in ("entrada", "saida"):
        raise HTTPException(status_code=400, detail="Tipo inválido")

    pool = get_pool()
    async with pool.acquire() as conn:
        # 1. Busca estoque atual
        estoque = await conn.fetchrow(
            "SELECT quantidade FROM estoque WHERE id = $1",
            mov.estoque_id
        )
        
        if estoque is None:
            raise HTTPException(status_code=404)

        # 2. Calcula nova quantidade
        nova_qtd = (
            estoque["quantidade"] + mov.quantidade
            if mov.tipo == "entrada"
            else estoque["quantidade"] - mov.quantidade
        )

        # 3. Valida saldo
        if nova_qtd < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Saldo insuficiente. Disponível: {estoque['quantidade']}"
            )

        # 4. Atualiza tudo em uma transação (seguro!)
        async with conn.transaction():
            await conn.execute(
                "UPDATE estoque SET quantidade = $1 WHERE id = $2",
                nova_qtd, mov.estoque_id
            )
            row = await conn.fetchrow(
                """
                INSERT INTO movimentacao_estoque (estoque_id, tipo, quantidade, observacao)
                VALUES ($1, $2, $3, $4)
                RETURNING *
                """,
                mov.estoque_id, mov.tipo, mov.quantidade, mov.observacao
            )

    return dict(row)
```

---

## 🐛 Debug

### Modo Debug FastAPI

```python
# No inicio de main.py, após criar a app:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="debug"  # ✅ Mostra mais detalhes
    )
```

### Adicionar Logs

```python
import logging

logger = logging.getLogger(__name__)

@app.post("/movimentacoes")
async def criar_movimentacao(mov: MovimentacaoCriar):
    logger.info(f"Criando movimentação: {mov.tipo} de {mov.quantidade} itens")
    # ... resto do código
    logger.debug(f"Nova quantidade: {nova_qtd}")
```

---

## 🔄 Fluxo de Commit de Código

1. **Faça mudanças** nos arquivos
2. **Teste localmente**
   ```bash
   uvicorn main:app --reload
   # Teste em http://localhost:8000/docs
   ```
3. **Verifique se não quebrou nada**
   - Endpoints antigos continuam funcionando?
   - Validações funcionam?
4. **Commit com mensagem descritiva**
   ```bash
   git add .
   git commit -m "feat: adiciona busca por nome de local"
   ```

---

## 🚀 Deploy para Produção

### Criar arquivo `.env` seguro (sem credenciais)

```bash
# .env.production
DATABASE_URL=postgresql://user:${DB_PASSWORD}@db.example.com:5432/estoque
```

### Rodar com Gunicorn + Uvicorn (mais estável)

```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📚 Recursos para Aprender

- [FastAPI Async SQL](https://fastapi.tiangolo.com/advanced/async-sql-databases/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/current/)
- [Pydantic Validators](https://docs.pydantic.dev/latest/concepts/validators/)
- [PostgreSQL Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)

---

## 🤝 Contribuindo

1. Crie uma branch: `git checkout -b feature/minha-feature`
2. Faça o desenvolvimento
3. Teste tudo: `uvicorn main:app --reload`
4. Commit: `git commit -m "feat: descrição da feature"`
5. Push: `git push origin feature/minha-feature`
6. Abra um Pull Request

---

## 📋 Checklist para Novo Endpoint

- [ ] Endpoint criado em `main.py`
- [ ] Modelo Pydantic criado em `schemas.py`
- [ ] Validações apropriadas
- [ ] Testado em http://localhost:8000/docs
- [ ] Trata erros corretamente (404, 400, etc)
- [ ] Query SQL segura contra SQL injection (usa `$1, $2...`)
- [ ] Documentação string adicionada (`""" Descrição """\`)
- [ ] Tags apropriadas para agrupar no Swagger

---

**Feliz codificação! 🎉**

Última atualização: 26 de maio de 2026
