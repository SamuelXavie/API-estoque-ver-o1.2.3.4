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

echo "🔍 Verificando credenciais do Supabase..."
python scripts/check_supabase.py || exit 1

# Iniciar servidor
PORT=${PORT:-8000}
BASE_PORT=$PORT

FREE_PORT=$(python - "$PORT" <<'PY'
import socket, sys
port_start = int(sys.argv[1])
for port in range(port_start, port_start + 10):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(('127.0.0.1', port))
            print(port)
            break
        except OSError:
            continue
else:
    raise SystemExit('Nenhuma porta livre encontrada entre {} e {}'.format(port_start, port_start + 9))
PY
)

PORT=$FREE_PORT

if [ "$PORT" != "$BASE_PORT" ]; then
    echo "⚠️  Porta $BASE_PORT ocupada. Iniciando em http://127.0.0.1:$PORT"
fi

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "🎉 API Iniciada!"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "📚 Documentação: http://127.0.0.1:$PORT/docs"
echo "🏠 Página Inicial: http://127.0.0.1:$PORT/"
echo "❤️  Health Check: http://127.0.0.1:$PORT/health"
echo ""
echo "Pressione Ctrl+C para parar..."
echo ""

uvicorn main:app --reload --host 127.0.0.1 --port "$PORT"
