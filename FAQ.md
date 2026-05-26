# ❓ FAQ - Perguntas Frequentes

## 📌 Índice Rápido

- [Instalação](#instalação)
- [Execução](#execução)
- [Banco de Dados](#banco-de-dados)
- [Endpoints](#endpoints)
- [Erros Comuns](#erros-comuns)

---

## Instalação

### P: Como instalar a API?

**R:** Siga estes passos:

```bash
cd estoque\ atualizado
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Veja [QUICK_START.md](QUICK_START.md) para mais detalhes.

---

### P: Posso usar Python 3.9?

**R:** A API foi testada em Python 3.10+. Python 3.9 pode funcionar, mas não é garantido. Use:

```bash
python3 --version  # Verifique sua versão
```

---

### P: E se eu não tiver `venv` instalado?

**R:** Instale o módulo:

```bash
# Ubuntu/Debian
sudo apt-get install python3-venv

# macOS
brew install python3

# Windows
# Python já vem com venv
```

---

## Execução

### P: Como rodar a API?

**R:** Ative o venv e execute:

```bash
source venv/bin/activate
uvicorn main:app --reload
```

A API estará em **http://localhost:8000**

---

### P: O que significa `--reload`?

**R:** Reinicia o servidor automaticamente quando você modifica os arquivos. Perfeito para desenvolvimento. Para produção, remova `--reload`.

---

### P: Como parar a API?

**R:** Pressione `Ctrl+C` no terminal.

---

### P: Como usar outra porta?

**R:** Use `--port`:

```bash
uvicorn main:app --reload --port 8001
```

---

### P: A API pode ficar rodando 24/7?

**R:** Sim! Use modo produção:

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

---

## Banco de Dados

### P: Qual banco de dados usar?

**R:** **PostgreSQL** é obrigatório. Versão 12+.

---

### P: Como instalar PostgreSQL?

**R:**

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

**macOS (com Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
[Download aqui](https://www.postgresql.org/download/windows/) e siga o instalador.

---

### P: Como criar o banco de dados?

**R:**

```bash
# Cria o banco
createdb -U postgres estoque_db

# Ou com psql
psql -U postgres
CREATE DATABASE estoque_db;
\q
```

---

### P: Qual é a senha padrão do PostgreSQL?

**R:** Durante a instalação, você cria a senha. Se esqueceu:

```bash
sudo -u postgres psql
ALTER USER postgres PASSWORD 'nova_senha';
```

---

### P: Como criar as tabelas?

**R:** Execute o SQL no `psql`:

```bash
psql -U postgres -d estoque_db

# Copie e cole o SQL (veja COMO_RODAR.md seção 5)
```

---

### P: Como fazer backup do banco?

**R:**

```bash
pg_dump -U postgres estoque_db > backup.sql
```

---

### P: Como restaurar um backup?

**R:**

```bash
psql -U postgres estoque_db < backup.sql
```

---

### P: A API funciona sem PostgreSQL?

**R:** Não. PostgreSQL é obrigatório. A API retornará erros se não conseguir conectar.

---

## Endpoints

### P: Como testar os endpoints?

**R:** Opções:

1. **Swagger UI** (Recomendado): http://localhost:8000/docs
2. **cURL**: `curl http://localhost:8000/locais`
3. **Postman**: Importe a collection
4. **Python requests**: Ver exemplos em [README.md](README.md)

---

### P: Como criar um local físico?

**R:**

```bash
curl -X POST http://localhost:8000/locais \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Prateleira A-1",
    "ativo": true
  }'
```

---

### P: Como registrar uma entrada de estoque?

**R:**

```bash
curl -X POST http://localhost:8000/movimentacoes \
  -H "Content-Type: application/json" \
  -d '{
    "estoque_id": "UUID_DO_ESTOQUE",
    "tipo": "entrada",
    "quantidade": 50,
    "observacao": "Recebimento NF-12345"
  }'
```

Substitua `UUID_DO_ESTOQUE` pelo ID do estoque.

---

### P: Como registrar uma saída?

**R:**

```bash
curl -X POST http://localhost:8000/movimentacoes \
  -H "Content-Type: application/json" \
  -d '{
    "estoque_id": "UUID_DO_ESTOQUE",
    "tipo": "saida",
    "quantidade": 20,
    "observacao": "Venda #001"
  }'
```

---

### P: Qual formato de UUID devo usar?

**R:** Formato padrão: `550e8400-e29b-41d4-a716-446655440000`

Gerar um:
```bash
# Linux/Mac
uuidgen

# Online: https://www.uuidgenerator.net/
```

---

### P: Como listar todos os registros?

**R:**

```bash
curl http://localhost:8000/locais
curl http://localhost:8000/estoques
curl http://localhost:8000/movimentacoes
```

---

### P: Como buscar por ID?

**R:**

```bash
curl http://localhost:8000/locais/550e8400-e29b-41d4-a716-446655440000
```

---

### P: Como atualizar um registro?

**R:**

```bash
curl -X PUT http://localhost:8000/locais/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Prateleira A-1 (Nova)"
  }'
```

---

### P: Como deletar um registro?

**R:**

```bash
curl -X DELETE http://localhost:8000/locais/550e8400-e29b-41d4-a716-446655440000
```

---

## Erros Comuns

### P: Erro: "Pool não inicializado"

**R:** O banco não está conectado.

**Solução:**
```bash
# Verifique se PostgreSQL está rodando
sudo service postgresql status

# Se não, inicie
sudo service postgresql start

# Verifique .env
cat .env
```

---

### P: Erro: "database does not exist"

**R:** O banco não foi criado.

**Solução:**
```bash
createdb -U postgres estoque_db
```

---

### P: Erro: "FATAL: Peer authentication failed"

**R:** PostgreSQL não está configurado para autenticação por senha.

**Solução:**

Edite `/etc/postgresql/*/main/pg_hba.conf` e mude:
```
# De:
local   all             postgres                                peer

# Para:
local   all             postgres                                md5
```

Depois reinicie:
```bash
sudo service postgresql restart
```

---

### P: Erro: "password authentication failed"

**R:** Senha errada no `.env`.

**Solução:**
1. Verifique a senha em `.env`
2. Ou redefina a senha:
```bash
sudo -u postgres psql
ALTER USER postgres PASSWORD 'nova_senha';
```

---

### P: Erro: "Porta 8000 em uso"

**R:** Outra aplicação está usando a porta.

**Solução:**
```bash
# Use outra porta
uvicorn main:app --reload --port 8001

# Ou mate o processo
lsof -i :8000
kill -9 <PID>
```

---

### P: Erro: "ModuleNotFoundError"

**R:** Virtualenv não está ativado ou dependências não instaladas.

**Solução:**
```bash
# Ative venv
source venv/bin/activate

# Reinstale
pip install -r requirements.txt
```

---

### P: Erro: "ImportError: cannot import name 'X'"

**R:** Há um erro no código.

**Solução:**
```bash
# Verifique a sintaxe
python3 -m py_compile main.py

# Ou use o linter
pip install flake8
flake8 main.py
```

---

### P: Erro 422: "Unprocessable Entity"

**R:** Dados inválidos na requisição.

**Verificação:**
- IDs estão em formato UUID válido?
- Números são números (não strings)?
- `tipo` é "entrada" ou "saida"?

---

### P: Erro 404: "Not Found"

**R:** Recurso não existe.

**Solução:**
- Verifique o ID está correto
- Use `GET /locais` para listar IDs válidos

---

### P: Erro 400: "Saldo insuficiente"

**R:** Tentou retirar mais do que tem em estoque.

**Solução:**
```bash
# Registre uma entrada primeiro
curl -X POST http://localhost:8000/movimentacoes \
  -H "Content-Type: application/json" \
  -d '{
    "estoque_id": "UUID",
    "tipo": "entrada",
    "quantidade": 100
  }'
```

---

### P: Erro: "UNIQUE constraint violated"

**R:** Um produto já existe no mesmo local.

**Solução:**
Cada produto só pode estar em um local. Se precisa em múltiplos locais, crie registros separados.

---

## Performance

### P: A API é rápida?

**R:** Sim! Com asyncpg e pool de conexões:
- Resposta média: < 50ms
- Suporta centenas de requisições/segundo

---

### P: Quantas conexões o pool tem?

**R:** Atualmente 1-5. Você pode ajustar em `database.py`:

```python
_pool = await asyncpg.create_pool(
    dsn=os.getenv("DATABASE_URL"),
    min_size=5,   # ← Aumentar aqui
    max_size=20,  # ← E aqui
)
```

---

## Desenvolvimento

### P: Como adicionar um novo endpoint?

**R:** Veja [DEVELOPMENT.md](DEVELOPMENT.md) seção "Adicionando um Novo Endpoint"

---

### P: Preciso de autenticação?

**R:** Não está implementada. Você pode adicionar usando:
- JWT tokens
- OAuth2
- API keys

Veja [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

### P: Como adicionar validações customizadas?

**R:** Use Pydantic validators em `schemas.py`:

```python
from pydantic import validator

class EstoqueCriar(BaseModel):
    quantidade: int
    quantidade_minima: int
    
    @validator('quantidade_minima')
    def validar_minima(cls, v, values):
        if 'quantidade' in values and v > values['quantidade']:
            raise ValueError('mínima não pode ser > quantidade')
        return v
```

---

### P: Como testar a API automaticamente?

**R:** Use pytest:

```bash
pip install pytest pytest-asyncio

# Crie tests/test_api.py
# Rode: pytest
```

---

## Deployment

### P: Como fazer deploy?

**R:** Varias opções:

1. **Heroku**:
   ```bash
   heroku create
   heroku config:set DATABASE_URL=...
   git push heroku main
   ```

2. **Docker**:
   ```bash
   docker build -t estoque-api .
   docker run -p 8000:8000 estoque-api
   ```

3. **VPS (Digital Ocean, AWS, etc)**:
   ```bash
   # SSH na máquina
   # Clone o repo
   # Configure como acima
   ```

---

### P: Como usar variáveis secretas?

**R:** Use `.env` (não versione):

```bash
# .env (não commitar)
DATABASE_URL=postgresql://user:secret@host/db
SECRET_KEY=sua_chave_secreta
```

Acesse em Python:
```python
import os
db_url = os.getenv("DATABASE_URL")
```

---

## Outras Dúvidas?

Verifique a documentação:
- [README.md](README.md) - Documentação principal
- [API_REFERENCE.md](API_REFERENCE.md) - Todos os endpoints
- [COMO_RODAR.md](COMO_RODAR.md) - Setup completo
- [DEVELOPMENT.md](DEVELOPMENT.md) - Desenvolvimento

---

**Última atualização:** 26 de maio de 2026

Não encontrou sua dúvida? Abra uma issue no repositório! 🚀
