# 📖 API Reference - Referência Completa de Endpoints

## Índice Rápido

- [Geral](#geral)
- [Local Físico](#local-físico)
- [Estoque](#estoque)
- [Movimentação](#movimentação)

---

## Geral

### GET `/`
**Descrição:** Verifica se a API está funcionando

**Request:**
```bash
curl http://localhost:8000/
```

**Response:** `200 OK`
```json
{
  "mensagem": "API de Estoque funcionando! Acesse /docs"
}
```

---

### GET `/health`
**Descrição:** Health check da API e conexão com banco

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:** `200 OK` (com banco conectado)
```json
{
  "status": "ok",
  "banco": "conectado"
}
```

**Response:** `200 OK` (sem banco)
```json
{
  "status": "erro",
  "detalhe": "Pool não inicializado"
}
```

---

## Local Físico

### GET `/locais`
**Descrição:** Lista todos os locais físicos

**Request:**
```bash
curl http://localhost:8000/locais
```

**Response:** `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nome": "Prateleira A-1",
    "descricao": "Primeiro andar, seção A",
    "ativo": true,
    "created_at": "2026-05-26T10:30:00"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "nome": "Galpão 1",
    "descricao": "Armazenagem grande",
    "ativo": true,
    "created_at": "2026-05-26T10:45:00"
  }
]
```

**Erros:**
- `500` - Erro no servidor ou banco de dados

---

### POST `/locais`
**Descrição:** Cria um novo local físico

**Request:**
```bash
curl -X POST http://localhost:8000/locais \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Prateleira A-1",
    "descricao": "Primeiro andar, seção A",
    "ativo": true
  }'
```

**Request Body:**
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| nome | string (max 100) | ✅ | Nome do local |
| descricao | string | ❌ | Descrição do local |
| ativo | boolean | ❌ | Status do local (padrão: true) |

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nome": "Prateleira A-1",
  "descricao": "Primeiro andar, seção A",
  "ativo": true,
  "created_at": "2026-05-26T10:30:00"
}
```

**Erros:**
- `422` - Validação de dados falhou
- `500` - Erro no servidor

---

### GET `/locais/{local_id}`
**Descrição:** Retorna um local específico

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| local_id | UUID | ID do local |

**Request:**
```bash
curl http://localhost:8000/locais/550e8400-e29b-41d4-a716-446655440000
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nome": "Prateleira A-1",
  "descricao": "Primeiro andar, seção A",
  "ativo": true,
  "created_at": "2026-05-26T10:30:00"
}
```

**Erros:**
- `404` - Local não encontrado

---

### PUT `/locais/{local_id}`
**Descrição:** Atualiza um local (apenas campos enviados são alterados)

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| local_id | UUID | ID do local |

**Request:**
```bash
curl -X PUT http://localhost:8000/locais/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Prateleira A-1 (Renovada)",
    "ativo": true
  }'
```

**Request Body (todos opcionais):**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| nome | string | Novo nome |
| descricao | string | Nova descrição |
| ativo | boolean | Novo status |

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nome": "Prateleira A-1 (Renovada)",
  "descricao": "Primeiro andar, seção A",
  "ativo": true,
  "created_at": "2026-05-26T10:30:00"
}
```

**Erros:**
- `400` - Nenhum campo enviado
- `404` - Local não encontrado

---

### DELETE `/locais/{local_id}`
**Descrição:** Remove um local físico

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| local_id | UUID | ID do local |

**Request:**
```bash
curl -X DELETE http://localhost:8000/locais/550e8400-e29b-41d4-a716-446655440000
```

**Response:** `200 OK`
```json
{
  "mensagem": "Local físico excluído com sucesso."
}
```

**Erros:**
- `404` - Local não encontrado
- `409` - Local possui estoque vinculado

---

## Estoque

### GET `/estoques`
**Descrição:** Lista todos os registros de estoque

**Request:**
```bash
curl http://localhost:8000/estoques
```

**Response:** `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440100",
    "produto_id": "550e8400-e29b-41d4-a716-446655440010",
    "local_id": "550e8400-e29b-41d4-a716-446655440000",
    "quantidade": 100,
    "quantidade_minima": 10,
    "quantidade_maxima": 500,
    "created_at": "2026-05-26T10:30:00"
  }
]
```

---

### POST `/estoques`
**Descrição:** Cria um novo registro de estoque

**Request:**
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

**Request Body:**
| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| produto_id | UUID | ✅ | - |
| local_id | UUID | ✅ | Deve existir |
| quantidade | integer | ✅ | >= 0 |
| quantidade_minima | integer | ❌ | >= 0 (padrão: 0) |
| quantidade_maxima | integer | ❌ | >= 0 |

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440100",
  "produto_id": "550e8400-e29b-41d4-a716-446655440010",
  "local_id": "550e8400-e29b-41d4-a716-446655440000",
  "quantidade": 100,
  "quantidade_minima": 10,
  "quantidade_maxima": 500,
  "created_at": "2026-05-26T10:30:00"
}
```

**Erros:**
- `422` - Validação falhou
- `500` - Erro no servidor

---

### GET `/estoques/{estoque_id}`
**Descrição:** Retorna um estoque específico

**Request:**
```bash
curl http://localhost:8000/estoques/550e8400-e29b-41d4-a716-446655440100
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440100",
  "produto_id": "550e8400-e29b-41d4-a716-446655440010",
  "local_id": "550e8400-e29b-41d4-a716-446655440000",
  "quantidade": 100,
  "quantidade_minima": 10,
  "quantidade_maxima": 500,
  "created_at": "2026-05-26T10:30:00"
}
```

**Erros:**
- `404` - Estoque não encontrado

---

### GET `/estoques/produto/{produto_id}`
**Descrição:** Lista todos os registros de um produto (pode estar em múltiplos locais)

**Request:**
```bash
curl http://localhost:8000/estoques/produto/550e8400-e29b-41d4-a716-446655440010
```

**Response:** `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440100",
    "produto_id": "550e8400-e29b-41d4-a716-446655440010",
    "local_id": "550e8400-e29b-41d4-a716-446655440000",
    "quantidade": 100,
    "quantidade_minima": 10,
    "quantidade_maxima": 500,
    "created_at": "2026-05-26T10:30:00"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440101",
    "produto_id": "550e8400-e29b-41d4-a716-446655440010",
    "local_id": "550e8400-e29b-41d4-a716-446655440001",
    "quantidade": 50,
    "quantidade_minima": 5,
    "quantidade_maxima": 200,
    "created_at": "2026-05-26T11:00:00"
  }
]
```

---

### PUT `/estoques/{estoque_id}`
**Descrição:** Atualiza um estoque

**Request:**
```bash
curl -X PUT http://localhost:8000/estoques/550e8400-e29b-41d4-a716-446655440100 \
  -H "Content-Type: application/json" \
  -d '{
    "quantidade": 150,
    "quantidade_minima": 15
  }'
```

**Request Body (todos opcionais):**
| Campo | Tipo | Validação |
|-------|------|-----------|
| produto_id | UUID | - |
| local_id | UUID | - |
| quantidade | integer | >= 0 |
| quantidade_minima | integer | >= 0 |
| quantidade_maxima | integer | >= 0 |

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440100",
  "produto_id": "550e8400-e29b-41d4-a716-446655440010",
  "local_id": "550e8400-e29b-41d4-a716-446655440000",
  "quantidade": 150,
  "quantidade_minima": 15,
  "quantidade_maxima": 500,
  "created_at": "2026-05-26T10:30:00"
}
```

---

### DELETE `/estoques/{estoque_id}`
**Descrição:** Remove um estoque (histórico de movimentações é mantido)

**Request:**
```bash
curl -X DELETE http://localhost:8000/estoques/550e8400-e29b-41d4-a716-446655440100
```

**Response:** `200 OK`
```json
{
  "mensagem": "Registro de estoque excluído com sucesso."
}
```

**Erros:**
- `404` - Estoque não encontrado

---

## Movimentação

### GET `/movimentacoes`
**Descrição:** Lista todas as movimentações (da mais recente para a mais antiga)

**Request:**
```bash
curl http://localhost:8000/movimentacoes
```

**Response:** `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440200",
    "estoque_id": "550e8400-e29b-41d4-a716-446655440100",
    "tipo": "saida",
    "quantidade": 20,
    "observacao": "Venda cliente #123",
    "created_at": "2026-05-26T11:00:00"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440201",
    "estoque_id": "550e8400-e29b-41d4-a716-446655440100",
    "tipo": "entrada",
    "quantidade": 50,
    "observacao": "Recebimento NF-12345",
    "created_at": "2026-05-26T10:30:00"
  }
]
```

---

### POST `/movimentacoes`
**Descrição:** Registra uma movimentação (entrada ou saída) e atualiza o estoque automaticamente

**Request - Entrada:**
```bash
curl -X POST http://localhost:8000/movimentacoes \
  -H "Content-Type: application/json" \
  -d '{
    "estoque_id": "550e8400-e29b-41d4-a716-446655440100",
    "tipo": "entrada",
    "quantidade": 50,
    "observacao": "Recebimento NF-12345"
  }'
```

**Request - Saída:**
```bash
curl -X POST http://localhost:8000/movimentacoes \
  -H "Content-Type: application/json" \
  -d '{
    "estoque_id": "550e8400-e29b-41d4-a716-446655440100",
    "tipo": "saida",
    "quantidade": 20,
    "observacao": "Venda cliente #123"
  }'
```

**Request Body:**
| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| estoque_id | UUID | ✅ | Deve existir |
| tipo | string | ✅ | "entrada" ou "saida" |
| quantidade | integer | ✅ | > 0 |
| observacao | string | ❌ | - |

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440200",
  "estoque_id": "550e8400-e29b-41d4-a716-446655440100",
  "tipo": "entrada",
  "quantidade": 50,
  "observacao": "Recebimento NF-12345",
  "created_at": "2026-05-26T10:30:00"
}
```

**Comportamento:**
- `tipo: "entrada"` → quantidade do estoque += quantidade
- `tipo: "saida"` → quantidade do estoque -= quantidade

**Erros:**
- `400` - Tipo inválido ou saldo insuficiente
- `404` - Estoque não encontrado
- `422` - Validação falhou

---

### GET `/movimentacoes/{movimentacao_id}`
**Descrição:** Retorna uma movimentação específica

**Request:**
```bash
curl http://localhost:8000/movimentacoes/550e8400-e29b-41d4-a716-446655440200
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440200",
  "estoque_id": "550e8400-e29b-41d4-a716-446655440100",
  "tipo": "entrada",
  "quantidade": 50,
  "observacao": "Recebimento NF-12345",
  "created_at": "2026-05-26T10:30:00"
}
```

**Erros:**
- `404` - Movimentação não encontrada

---

### GET `/movimentacoes/estoque/{estoque_id}`
**Descrição:** Lista todas as movimentações de um estoque

**Request:**
```bash
curl http://localhost:8000/movimentacoes/estoque/550e8400-e29b-41d4-a716-446655440100
```

**Response:** `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440200",
    "estoque_id": "550e8400-e29b-41d4-a716-446655440100",
    "tipo": "saida",
    "quantidade": 20,
    "observacao": "Venda cliente #123",
    "created_at": "2026-05-26T11:00:00"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440201",
    "estoque_id": "550e8400-e29b-41d4-a716-446655440100",
    "tipo": "entrada",
    "quantidade": 50,
    "observacao": "Recebimento NF-12345",
    "created_at": "2026-05-26T10:30:00"
  }
]
```

---

### PUT `/movimentacoes/{movimentacao_id}`
**Descrição:** Atualiza tipo ou observação (não altera a quantidade)

**Request:**
```bash
curl -X PUT http://localhost:8000/movimentacoes/550e8400-e29b-41d4-a716-446655440200 \
  -H "Content-Type: application/json" \
  -d '{
    "observacao": "Observação corrigida",
    "tipo": "entrada"
  }'
```

**Request Body (todos opcionais):**
| Campo | Tipo | Validação |
|-------|------|-----------|
| tipo | string | "entrada" ou "saida" |
| observacao | string | - |

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440200",
  "estoque_id": "550e8400-e29b-41d4-a716-446655440100",
  "tipo": "entrada",
  "quantidade": 50,
  "observacao": "Observação corrigida",
  "created_at": "2026-05-26T10:30:00"
}
```

---

### DELETE `/movimentacoes/{movimentacao_id}`
**Descrição:** Remove uma movimentação do histórico (⚠️ não reverte o saldo)

**Request:**
```bash
curl -X DELETE http://localhost:8000/movimentacoes/550e8400-e29b-41d4-a716-446655440200
```

**Response:** `200 OK`
```json
{
  "mensagem": "Movimentação excluída do histórico com sucesso."
}
```

**⚠️ Aviso:** Deletar uma movimentação não reverte a quantidade do estoque. Use com cuidado!

**Erros:**
- `404` - Movimentação não encontrada

---

## Status HTTP

| Código | Significado |
|--------|-------------|
| **200** | ✅ OK - Requisição bem-sucedida |
| **201** | ✅ Created - Recurso criado |
| **400** | ❌ Bad Request - Dados inválidos |
| **404** | ❌ Not Found - Recurso não encontrado |
| **422** | ❌ Unprocessable Entity - Validação falhou |
| **500** | ❌ Internal Server Error - Erro no servidor |

---

**Última atualização:** 26 de maio de 2026
