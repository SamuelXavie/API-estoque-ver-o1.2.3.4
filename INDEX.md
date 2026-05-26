# 📚 Índice de Documentação

Bem-vindo! Aqui você encontra toda a documentação da **API de Estoque**.

---

## 🚀 Começar Rápido

Novo na API? Comece por aqui:

1. **[QUICK_START.md](QUICK_START.md)** ⚡ 
   - Setup em 5 minutos
   - Comandos básicos
   - Primeiros testes

2. **[COMO_RODAR.md](COMO_RODAR.md)** 🏃
   - Setup completo passo a passo
   - Criar banco de dados
   - Exemplos de requisições

---

## 📖 Documentação Completa

### [README.md](README.md) 📦
**Documentação principal da API**

Contém:
- Visão geral do projeto
- Arquitetura
- Instalação
- Execução
- Documentação básica de endpoints
- Regras importantes
- Troubleshooting

**Leia se:** Você quer entender o que é a API

---

### [API_REFERENCE.md](API_REFERENCE.md) 📘
**Referência completa de todos os endpoints**

Contém:
- GET `/` - Raiz da API
- GET `/health` - Status
- **Local Físico** (5 endpoints)
- **Estoque** (6 endpoints)
- **Movimentação** (6 endpoints)
- Códigos HTTP
- Exemplos de requisição e resposta

**Leia se:** Você precisa consultar um endpoint específico

---

## 🛠️ Desenvolvimento

### [DEVELOPMENT.md](DEVELOPMENT.md) 🔧
**Guia para desenvolvedores que querem contribuir**

Contém:
- Setup de desenvolvimento
- Estrutura dos arquivos
- Como adicionar endpoints
- Testando endpoints
- Fluxo de movimentação
- Debug
- Validações
- Lógica de negócio
- Checklist para novo endpoint

**Leia se:** Você quer adicionar ou modificar a API

---

## ❓ Dúvidas e Suporte

### [FAQ.md](FAQ.md) ❓
**Perguntas Frequentes**

Organizado por categorias:
- **Instalação**: 6 dúvidas
- **Execução**: 8 dúvidas
- **Banco de Dados**: 10 dúvidas
- **Endpoints**: 12 dúvidas
- **Erros Comuns**: 15 dúvidas
- **Performance**: 2 dúvidas
- **Desenvolvimento**: 4 dúvidas
- **Deployment**: 4 dúvidas

**Leia se:** Você tem uma dúvida rápida

---

## 📁 Estrutura do Projeto

```
estoque_api/
├── 📄 README.md              ← Comece aqui!
├── 📄 QUICK_START.md         ← Setup rápido
├── 📄 COMO_RODAR.md          ← Setup completo
├── 📄 API_REFERENCE.md       ← Referência de endpoints
├── 📄 DEVELOPMENT.md         ← Desenvolvimento
├── 📄 FAQ.md                 ← Perguntas frequentes
├── 📄 INDEX.md               ← Este arquivo
│
├── 🐍 main.py                ← Rotas (endpoints)
├── 🐍 database.py            ← Conexão PostgreSQL
├── 🐍 schemas.py             ← Modelos Pydantic
│
├── 📦 requirements.txt        ← Dependências
├── 🔐 .env.example           ← Template de variáveis
├── 🔐 .env                   ← Variáveis (não versionar)
├── 🚀 start.sh               ← Script de execução
│
└── venv/                     ← Ambiente virtual
```

---

## 🎯 Roadmap de Leitura

### Para Usuários da API

1. [QUICK_START.md](QUICK_START.md) - Setup rápido (5 min)
2. [README.md](README.md) - Visão geral (10 min)
3. [API_REFERENCE.md](API_REFERENCE.md) - Consultar endpoints (conforme necessário)
4. [FAQ.md](FAQ.md) - Se tiver dúvidas (conforme necessário)

**Tempo total:** ~15 minutos

---

### Para Desenvolvedores

1. [QUICK_START.md](QUICK_START.md) - Setup (5 min)
2. [DEVELOPMENT.md](DEVELOPMENT.md) - Desenvolvimento (20 min)
3. [API_REFERENCE.md](API_REFERENCE.md) - Referência (10 min)
4. [FAQ.md](FAQ.md) - Dúvidas técnicas (conforme necessário)

**Tempo total:** ~35 minutos

---

### Para DevOps/Infrastructure

1. [README.md](README.md#-executando-a-api) - Execução (5 min)
2. [COMO_RODAR.md](COMO_RODAR.md) - Setup completo (15 min)
3. [FAQ.md](FAQ.md#deployment) - Deployment (10 min)

**Tempo total:** ~30 minutos

---

## 🔍 Busca Rápida

### Quero... (Clique para ir direto)

**Setup & Instalação**
- [Como instalar?](QUICK_START.md#️-setup-inicial)
- [Como rodar?](QUICK_START.md#️-rodar-a-api)
- [Como acessar?](QUICK_START.md#-acessar-a-api)

**Usar a API**
- [Listar locais](API_REFERENCE.md#get-locais)
- [Criar estoque](API_REFERENCE.md#post-estoques)
- [Registrar movimentação](API_REFERENCE.md#post-movimentacoes)

**Entender a API**
- [Visão geral](README.md#-visão-geral)
- [Arquitetura](README.md#-arquitetura)
- [Modelos de dados](README.md#-modelos-de-dados)

**Desenvolver**
- [Adicionar endpoint](DEVELOPMENT.md#️-adicionando-um-novo-endpoint)
- [Debug](DEVELOPMENT.md#-debug)
- [Contribuir](DEVELOPMENT.md#-fluxo-de-commit-de-código)

**Resolver Problemas**
- [Erros comuns](README.md#-troubleshooting)
- [FAQ](FAQ.md)

---

## 📊 Documentação por Tipo

### 📘 Tutorial (Aprenda)
- [QUICK_START.md](QUICK_START.md)
- [COMO_RODAR.md](COMO_RODAR.md)

### 📖 Referência (Consulte)
- [README.md](README.md)
- [API_REFERENCE.md](API_REFERENCE.md)

### 🔧 How-To (Faça)
- [DEVELOPMENT.md](DEVELOPMENT.md)
- [FAQ.md](FAQ.md)

---

## 🎓 Conceitos Principais

### Três Recursos Principais

1. **Local Físico** - Onde os itens são armazenados
   ```
   prateleira, galpão, caixa, etc.
   ```

2. **Estoque** - Produto em um local específico
   ```
   { produto_id, local_id, quantidade }
   ```

3. **Movimentação** - Registro de entrada/saída
   ```
   entrada (+qtd) ou saida (-qtd)
   ```

### Fluxo Principal

```
1. Criar Local Físico
   ↓
2. Criar Estoque (vincular produto + local)
   ↓
3. Registrar Movimentações (entrada/saída)
   ↓
4. Consultar histórico
```

Veja [README.md#exemplos-de-uso](README.md#exemplos-de-uso) para exemplo prático.

---

## 🌐 Acessar a API

Quando estiver rodando:

- **Swagger UI (Teste interativo)**: http://localhost:8000/docs ✅ **Use isto!**
- **ReDoc (Documentação)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Raiz**: http://localhost:8000/

---

## 📞 Suporte

**Não encontrou o que procura?**

1. Procure no [FAQ.md](FAQ.md)
2. Consulte [API_REFERENCE.md](API_REFERENCE.md)
3. Leia [DEVELOPMENT.md](DEVELOPMENT.md)
4. Abra uma issue no repositório

---

## 📝 Changelog

| Versão | Data | Mudanças |
|--------|------|----------|
| 2.0.0 | 26/05/2026 | Documentação completa |
| 1.0.0 | XX/XX/2026 | Versão inicial |

---

## ✅ Checklist: "Estou Pronto?"

- [ ] Li [QUICK_START.md](QUICK_START.md)
- [ ] Instalei as dependências
- [ ] Criei o banco de dados
- [ ] Rodei a API (`uvicorn main:app --reload`)
- [ ] Acessei http://localhost:8000/docs
- [ ] Testei um endpoint
- [ ] Consultei [API_REFERENCE.md](API_REFERENCE.md) para mais endpoints

**Se marcou tudo:** Você está pronto! 🚀

---

## 🎯 Próximos Passos

### Iniciante
1. Customize o `.env` com suas credenciais
2. Explore os endpoints no Swagger UI
3. Leia [FAQ.md](FAQ.md) conforme surgirem dúvidas

### Desenvolvedor
1. Clone o repositório
2. Setup de desenvolvimento ([DEVELOPMENT.md](DEVELOPMENT.md))
3. Faça suas mudanças
4. Teste tudo
5. Commit e push

### DevOps
1. Configure o `.env` para produção
2. Prepare o banco de dados
3. Deploy (veja [FAQ.md#deployment](FAQ.md#deployment))
4. Configure backups automatizados

---

## 🔗 Links Úteis

**Documentação Oficial**
- [FastAPI](https://fastapi.tiangolo.com/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [asyncpg](https://magicstack.github.io/asyncpg/)
- [Pydantic](https://docs.pydantic.dev/)

**Ferramentas**
- [Swagger/OpenAPI](https://swagger.io/)
- [Postman](https://www.postman.com/)
- [pgAdmin](https://www.pgadmin.org/) - Interface PostgreSQL

---

**Última atualização:** 26 de maio de 2026

Bem-vindo à API de Estoque! 🎉
