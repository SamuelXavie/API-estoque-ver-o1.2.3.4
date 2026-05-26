#!/bin/bash

# 🚀 Script para rodar a API de Estoque localmente
# Use: ./start.sh

set -e  # Parar em caso de erro

echo "════════════════════════════════════════════════════════════"
echo "🚀 Iniciando API de Estoque"
echo "════════════════════════════════════════════════════════════"

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📝 Copiando de .env.example..."
    cp .env.example .env
    echo "✅ Arquivo .env criado. Edite com suas credenciais do PostgreSQL."
    exit 1
fi

# Verificar se virtualenv existe, se não criar
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
fi

# Ativar virtualenv
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -q -r requirements.txt
echo "✅ Dependências instaladas"

# Verificar conexão com PostgreSQL
echo "🔍 Verificando conexão com PostgreSQL..."
python -c "
import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def check_db():
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        await conn.close()
        print('✅ Banco de dados conectado!')
        return True
    except Exception as e:
        print(f'❌ Erro ao conectar: {e}')
        return False

result = asyncio.run(check_db())
exit(0 if result else 1)
" || exit 1

# Iniciar servidor
echo ""
echo "════════════════════════════════════════════════════════════"
echo "🎉 API Iniciada!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📚 Documentação: http://localhost:8000/docs"
echo "🏠 Página Inicial: http://localhost:8000/"
echo "❤️  Health Check: http://localhost:8000/health"
echo ""
echo "Pressione Ctrl+C para parar..."
echo ""

uvicorn main:app --reload
