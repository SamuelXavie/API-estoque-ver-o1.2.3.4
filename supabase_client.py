import os
from typing import Optional
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

_supabase = None


def criar_supabase():
    try:
        from supabase import create_client
    except Exception as e:
        raise RuntimeError(
            "Biblioteca supabase não encontrada. Instale com: pip install supabase"
        ) from e

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL e SUPABASE_KEY (ou SUPABASE_SERVICE_ROLE_KEY) devem estar definidos no .env")

    if os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        print("✅ Usando SUPABASE_SERVICE_ROLE_KEY para ações de backend.")
    else:
        print("⚠️  Usando SUPABASE_KEY em modo fallback. Pode falhar se o RLS estiver ativo.")

    global _supabase
    _supabase = create_client(url, key)


def fechar_supabase():
    # supabase-py não exige fechamento explícito; placeholder
    global _supabase
    _supabase = None


def get_supabase():
    if _supabase is None:
        raise RuntimeError("Supabase client não inicializado. Verifique startup da aplicação.")
    return _supabase
