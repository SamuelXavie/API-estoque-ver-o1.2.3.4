# 🚀 API de Estoque - Guia de Execução Local

## 📋 Pré-requisitos

- Python 3.10+
- PostgreSQL instalado e rodando
- pip (gerenciador de pacotes Python)

---

## 1️⃣ Clonar/Preparar o Projeto

```bash
cd /home/samu/estoque\ atualizado\ \(1\)
```

---

## 2️⃣ Criar Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas credenciais do PostgreSQL
# Exemplo de conteúdo para .env:
# DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/estoque_db
```

---

## 3️⃣ Instalar Dependências

```bash
# Opção 1: Instalar direto (sem ambiente virtual)
pip install -r requirements.txt

# Opção 2: Com venv (recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 4️⃣ Criar Banco de Dados (PostgreSQL)

```bash
# Conectar ao PostgreSQL
psql -U postgres

# Dentro do psql:
CREATE DATABASE estoque_db;
\q
```

---

## 5️⃣ Criar as Tabelas no Banco

```sql
-- Copie e execute no PostgreSQL:

CREATE TABLE local_fisico (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE estoque (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    produto_id UUID NOT NULL,
    local_id UUID NOT NULL REFERENCES local_fisico(id),
    quantidade INT NOT NULL DEFAULT 0,
    quantidade_minima INT DEFAULT 0,
    quantidade_maxima INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT estoque_produto_local_unique UNIQUE(produto_id, local_id)
);

CREATE TABLE movimentacao_estoque (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estoque_id UUID NOT NULL REFERENCES estoque(id),
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('entrada', 'saida')),
    quantidade INT NOT NULL CHECK (quantidade > 0),
    observacao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_estoque_produto ON estoque(produto_id);
CREATE INDEX idx_estoque_local ON estoque(local_id);
CREATE INDEX idx_movimentacao_estoque ON movimentacao_estoque(estoque_id);
```

---

## 6️⃣ Rodar a API

```bash
# Modo desenvolvimento (com auto-reload)
uvicorn main:app --reload

# Modo produção (sem auto-reload)
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 7️⃣ Acessar a API

- 📚 **Documentação Interativa (Swagger):** http://localhost:8000/docs
- 🔍 **Documentação Alternativa (ReDoc):** http://localhost:8000/redoc
- ❤️ **Health Check:** http://localhost:8000/health
- 🏠 **Página Inicial:** http://localhost:8000/

---

## 📝 Exemplos de Requisições

### 1. Criar um Local Físico

```bash
curl -X POST http://localhost:8000/locais \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Prateleira A-1",
    "descricao": "Primeiro andar, seção A",
    "ativo": true
  }'
```

### 2. Criar um Registro de Estoque

```bash
curl -X POST http://localhost:8000/estoques \
  -H "Content-Type: application/json" \
  -d '{
    "produto_id": "550e8400-e29b-41d4-a716-446655440000",
    "local_id": "550e8400-e29b-41d4-a716-446655440001",
    "quantidade": 100,
    "quantidade_minima": 10,
    "quantidade_maxima": 500
  }'
```

### 3. Registrar Entrada de Estoque

```bash
curl -X POST http://localhost:8000/movimentacoes \
  -H "Content-Type: application/json" \
  -d '{
    "estoque_id": "550e8400-e29b-41d4-a716-446655440002",
    "tipo": "entrada",
    "quantidade": 50,
    "observacao": "Recebimento da nota fiscal NF-12345"
  }'
```

### 4. Registrar Saída de Estoque

```bash
curl -X POST http://localhost:8000/movimentacoes \
  -H "Content-Type: application/json" \
  -d '{
    "estoque_id": "550e8400-e29b-41d4-a716-446655440002",
    "tipo": "saida",
    "quantidade": 20,
    "observacao": "Venda para cliente #123"
  }'
```

---

## ⚠️ Troubleshooting

### Erro: "Pool não inicializado"
- ✅ Verifique se o banco PostgreSQL está rodando
- ✅ Verifique se `DATABASE_URL` no `.env` está correto

### Erro: "FATAL: database does not exist"
- ✅ Crie o banco: `createdb -U postgres estoque_db`

### Erro: "connection refused"
- ✅ Inicie PostgreSQL: `sudo service postgresql start` (Linux)
- ✅ Ou: `brew services start postgresql` (macOS)

---

## 📦 Dependências Instaladas

- **fastapi==0.115.12** - Framework web assíncrono
- **uvicorn==0.34.0** - Servidor ASGI
- **asyncpg==0.30.0** - Driver PostgreSQL assíncrono
- **python-dotenv==1.1.0** - Carregamento de variáveis de ambiente

---

## 🛑 Para a API

```bash
# Pressione Ctrl+C no terminal
```

---

**Feito! 🎉 Sua API está rodando em `http://localhost:8000`**
