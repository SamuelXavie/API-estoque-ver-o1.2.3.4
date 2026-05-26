# 📦 API de Estoque

> Sistema de Gerenciamento de Estoque, Locais Físicos e Movimentações

**Versão:** 2.0.0 | **Disciplina:** Sistemas Distribuídos - Etapa 3

---

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Início Rápido](#início-rápido)
- [Instalação](#instalação)
- [Executando a API](#executando-a-api)
- [Documentação de Endpoints](#documentação-de-endpoints)
- [Exemplos de Uso](#exemplos-de-uso)
- [Regras Importantes](#regras-importantes)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

API REST construída com **FastAPI** e **PostgreSQL** para gerenciar:

- **Local Físico** - Locais de armazenagem (prateleiras, galpões, etc.)
- **Estoque** - Produtos armazenados em locais específicos  
- **Movimentação** - Registros de entrada e saída de itens

### 📁 Estrutura do Projeto

```
estoque_api/
├── main.py              # Rotas da API (endpoints)
├── database.py          # Conexão com PostgreSQL
├── schemas.py           # Modelos Pydantic
├── requirements.txt     # Dependências
├── .env.example         # Template de variáveis
├── README.md            # Documentação (este arquivo)
├── COMO_RODAR.md        # Guia completo de setup
└── QUICK_START.md       # Início rápido
```

---

## ⚡ Início Rápido

### 1️⃣ Pré-requisitos
- Python 3.10+
- PostgreSQL 12+
- pip

### 2️⃣ Setup
```bash
cd estoque\ atualizado
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3️⃣ Configurar Banco
```bash
cp .env.example .env
# Edite .env com suas credenciais
createdb estoque_db
```

### 4️⃣ Rodar a API
```bash
uvicorn main:app --reload
```

### 5️⃣ Acessar
🌐 **http://localhost:8000/docs** - Swagger UI (teste aqui!)

---

## 💻 Instalação Completa

### Passo 1: Ambiente Virtual
```bash
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# ou
venv\Scripts\activate           # Windows
```

### Passo 2: Dependências
```bash
pip install -r requirements.txt
```

**Pacotes instalados:**
- `fastapi` - Framework web assíncrono
- `uvicorn` - Servidor ASGI
- `asyncpg` - Driver PostgreSQL assíncrono
- `python-dotenv` - Carregamento de variáveis

### Passo 3: Variáveis de Ambiente
```bash
cp .env.example .env
# Edite .env:
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/estoque_db
```

### Passo 4: Banco de Dados
```bash
createdb -U postgres estoque_db
```

### Passo 5: Criar Tabelas
```bash
psql -U postgres -d estoque_db
```

Cole o SQL:
```sql
CREATE TABLE IF NOT EXISTS local_fisico (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS estoque (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    produto_id UUID NOT NULL,
    local_id UUID NOT NULL REFERENCES local_fisico(id),
    quantidade INT NOT NULL DEFAULT 0,
    quantidade_minima INT DEFAULT 0,
    quantidade_maxima INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT estoque_produto_local_unique UNIQUE(produto_id, local_id)
);

CREATE TABLE IF NOT EXISTS movimentacao_estoque (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estoque_id UUID NOT NULL REFERENCES estoque(id),
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('entrada', 'saida')),
    quantidade INT NOT NULL CHECK (quantidade > 0),
    observacao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_estoque_produto ON estoque(produto_id);
CREATE INDEX IF NOT EXISTS idx_estoque_local ON estoque(local_id);
CREATE INDEX IF NOT EXISTS idx_movimentacao_estoque ON movimentacao_estoque(estoque_id);
```

---

## 🚀 Executando a API

### Modo Desenvolvimento
```bash
source venv/bin/activate
uvicorn main:app --reload
```

**Output esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process
```

### Modo Produção
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Script Automatizado
```bash
./start.sh
```

---

## 📚 Documentação de Endpoints

### 🏠 Endpoints Gerais

#### `GET /`
Verifica se a API está funcionando.

```bash
curl http://localhost:8000/
```

**Response:**
```json
{ "mensagem": "API de Estoque funcionando! Acesse /docs" }
```

#### `GET /health`
Health check com status do banco.

```bash
curl http://localhost:8000/health
```

**Response (banco conectado):**
```json
{ "status": "ok", "banco": "conectado" }
```

---

### 🏢 Local Físico

#### `GET /locais`
Lista todos os locais.

```bash
curl http://localhost:8000/locais
```

#### `POST /locais`
Cria um novo local.

```bash
curl -X POST http://localhost:8000/locais \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Prateleira A-1",
    "descricao": "Primeiro andar",
    "ativo": true
  }'
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nome": "Prateleira A-1",
  "descricao": "Primeiro andar",
  "ativo": true,
  "created_at": "2026-05-26T10:30:00"
}
```

#### `GET /locais/{local_id}`
Busca um local específico.

```bash
curl http://localhost:8000/locais/550e8400-e29b-41d4-a716-446655440000
```

#### `PUT /locais/{local_id}`
Atualiza um local.

```bash
curl -X PUT http://localhost:8000/locais/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{ "nome": "Prateleira A-1 (Renovada)" }'
```

#### `DELETE /locais/{local_id}`
Deleta um local.

```bash
curl -X DELETE http://localhost:8000/locais/550e8400-e29b-41d4-a716-446655440000
```

---

### 📦 Estoque

#### `GET /estoques`
Lista todos os estoques.

#### `POST /estoques`
Cria um novo registro de estoque.

```bash
curl -X POST http://localhost:8000/estoques \
  -H "Content-Type: application/json" \
  -d '{
    "produto_id": "550e8400-e29b-41d4-a716-446655440010",
    "local_id": "550e8400-e29b-41d4-a716-446655440000",
    "quantidade": 100,
    "quantidade_minima": 10,
    "quantidade_maxima": 500
  }'
```

#### `GET /estoques/{estoque_id}`
Busca um estoque específico.

#### `GET /estoques/produto/{produto_id}`
Lista estoques de um produto (pode estar em múltiplos locais).

#### `PUT /estoques/{estoque_id}`
Atualiza um estoque.

#### `DELETE /estoques/{estoque_id}`
Deleta um estoque.

---

### 📊 Movimentação

#### `GET /movimentacoes`
Lista todas as movimentações.

#### `POST /movimentacoes`
Registra uma entrada ou saída (atualiza estoque automaticamente).

**Entrada:**
```bash
curl -X POST http://localhost:8000/movimentacoes \
  -H "Content-Type: application/json" \
  -d '{
    "estoque_id": "550e8400-e29b-41d4-a716-446655440001",
    "tipo": "entrada",
    "quantidade": 50,
    "observacao": "Recebimento NF-12345"
  }'
```

**Saída:**
```bash
curl -X POST http://localhost:8000/movimentacoes \
  -H "Content-Type: application/json" \
  -d '{
    "estoque_id": "550e8400-e29b-41d4-a716-446655440001",
    "tipo": "saida",
    "quantidade": 20,
    "observacao": "Venda cliente #123"
  }'
```

#### `GET /movimentacoes/{movimentacao_id}`
Busca uma movimentação.

#### `GET /movimentacoes/estoque/{estoque_id}`
Lista movimentações de um estoque.

#### `PUT /movimentacoes/{movimentacao_id}`
Atualiza tipo ou observação.

#### `DELETE /movimentacoes/{movimentacao_id}`
Deleta uma movimentação.

---

## 💡 Exemplos de Uso

### Python com Requests
```python
import requests

API = "http://localhost:8000"

# Criar local
local = requests.post(f"{API}/locais", json={
    "nome": "Galpão 1",
    "ativo": True
}).json()
print(f"Local: {local['id']}")

# Criar estoque
estoque = requests.post(f"{API}/estoques", json={
    "produto_id": "550e8400-e29b-41d4-a716-446655440010",
    "local_id": local['id'],
    "quantidade": 100
}).json()
print(f"Estoque: {estoque['id']}")

# Entrada
entrada = requests.post(f"{API}/movimentacoes", json={
    "estoque_id": estoque['id'],
    "tipo": "entrada",
    "quantidade": 50,
    "observacao": "Compra #001"
}).json()
print(f"Entrada registrada")

# Saída
saida = requests.post(f"{API}/movimentacoes", json={
    "estoque_id": estoque['id'],
    "tipo": "saida",
    "quantidade": 20,
    "observacao": "Venda #001"
}).json()
print(f"Saída registrada")

# Listar movimentações
movs = requests.get(f"{API}/movimentacoes/estoque/{estoque['id']}").json()
print(f"Total de movimentações: {len(movs)}")
```

---

## ⚠️ Regras Importantes

### 🚫 Quantidade nunca fica negativa
Se tentar dar saída de mais itens do que o estoque tem, a API retorna erro 400:
```json
{
  "detail": "Saldo insuficiente. Disponível: 50, solicitado: 100."
}
```

### 🏠 Locais com estoque não podem ser deletados
Remova o estoque primeiro.

### 🔁 Movimentações precisam de tipo válido
Apenas `entrada` ou `saida` são aceitos.

### 📝 UUIDs obrigatórios
Use UUIDs válidos para `produto_id` e `local_id`.

---

## 🚨 Codes de Status HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Requisição bem-sucedida |
| 201 | Created - Recurso criado |
| 400 | Bad Request - Dados inválidos |
| 404 | Not Found - Recurso não encontrado |
| 422 | Unprocessable Entity - Validação falhou |
| 500 | Server Error - Erro no servidor |

---

## 🔧 Troubleshooting

### ❌ "Pool não inicializado"
```bash
# Verifique se PostgreSQL está rodando
sudo service postgresql status

# Se não, inicie:
sudo service postgresql start
```

### ❌ "database does not exist"
```bash
createdb -U postgres estoque_db
```

### ❌ "Porta 8000 em uso"
```bash
# Use outra porta
uvicorn main:app --reload --port 8001
```

### ❌ "ModuleNotFoundError: No module named 'fastapi'"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📖 Documentação Adicional

- [COMO_RODAR.md](COMO_RODAR.md) - Guia completo de setup
- [QUICK_START.md](QUICK_START.md) - Início rápido
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

**Última atualização:** 26 de maio de 2026


