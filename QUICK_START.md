# 📦 API de Estoque - Guia Rápido

## ⚡ Comandos Principais

### 1. Primeira Execução (Setup Completo)

```bash
# Copiar variáveis de ambiente
cp .env.example .env

# Editar .env com credenciais do PostgreSQL
nano .env

# Criar ambiente virtual
python3 -m venv venv

# Ativar venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Criar Banco de Dados

```bash
# No terminal PostgreSQL (psql):
psql -U postgres

# Dentro do psql:
CREATE DATABASE estoque_db;
\q

# Executar script SQL para criar tabelas (veja COMO_RODAR.md)
```

### 3. Rodar a API

**Opção A - Script Automatizado (Recomendado):**
```bash
./start.sh
```

**Opção B - Comando Manual:**
```bash
source venv/bin/activate
uvicorn main:app --reload
```

---

## 🌐 Acessar a API

Após iniciar a API, acesse:

| URL | Descrição |
|-----|-----------|
| http://localhost:8000/docs | 📚 Swagger UI (melhor para testar) |
| http://localhost:8000/redoc | 🔍 ReDoc (documentação em leitura) |
| http://localhost:8000/health | ❤️ Status da API |
| http://localhost:8000/ | 🏠 Página inicial |

---

## 📋 Estrutura do Projeto

```
├── main.py              # 🎯 Arquivo principal com as rotas
├── database.py          # 🗄️ Configuração do pool PostgreSQL
├── schemas.py           # 📝 Modelos Pydantic
├── requirements.txt     # 📦 Dependências
├── .env.example         # 🔐 Template de variáveis
├── COMO_RODAR.md       # 📖 Guia completo
├── QUICK_START.md      # ⚡ Este arquivo
└── start.sh            # 🚀 Script de execução
```

---

## 🧪 Testar Endpoints

Use a interface Swagger em `http://localhost:8000/docs` ou curl:

```bash
# Health Check
curl http://localhost:8000/health

# Listar locais
curl http://localhost:8000/locais

# Listar estoques
curl http://localhost:8000/estoques

# Listar movimentações
curl http://localhost:8000/movimentacoes
```

---

## 🐛 Erros Comuns

| Erro | Solução |
|------|---------|
| `Pool não inicializado` | PostgreSQL não está rodando ou URL errada em `.env` |
| `database does not exist` | Rode: `createdb -U postgres estoque_db` |
| `connection refused` | Inicie PostgreSQL: `sudo service postgresql start` |

---

## 📚 Documentação Completa

Veja [COMO_RODAR.md](COMO_RODAR.md) para:
- Setup passo a passo
- SQL para criar tabelas
- Exemplos de requisições
- Troubleshooting detalhado

---

## 🛑 Parar a API

```bash
Pressione Ctrl+C no terminal
```

---

**Pronto! Você tem uma API FastAPI + PostgreSQL rodando localmente! 🎉**
