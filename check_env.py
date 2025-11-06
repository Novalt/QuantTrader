# check_env.py - VERIFICADOR DE CONFIGURAÇÕES
import os
from dotenv import load_dotenv

load_dotenv()

def check_environment():
    print("🔍 VERIFICANDO CONFIGURAÇÕES DO .env")
    print("=" * 50)
    
    required_vars = [
        'ALPHA_VANTAGE_API_KEY',
        'FRED_API_KEY'
    ]
    
    optional_vars = [
        'BRAPI_API_KEY',
        'STOCKS_BR',
        'FOREX_PAIRS'
    ]
    
    # Verificar variáveis obrigatórias
    print("\n✅ VARIÁVEIS OBRIGATÓRIAS:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✓ {var}: Configurada")
        else:
            print(f"  ✗ {var}: NÃO CONFIGURADA!")
    
    # Verificar variáveis opcionais
    print("\n📋 VARIÁVEIS OPCIONAIS:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✓ {var}: {value}")
        else:
            print(f"  ○ {var}: Não configurada (opcional)")
    
    print("\n" + "=" * 50)
    
    # Verificação final
    missing_required = [var for var in required_vars if not os.getenv(var)]
    if missing_required:
        print(f"❌ FALTAM CONFIGURAÇÕES: {', '.join(missing_required)}")
        return False
    else:
        print("✅ TODAS CONFIGURAÇÕES ESSENCIAIS OK!")
        return True

if __name__ == "__main__":
    success = check_environment()
    if not success:
        print("\n💡 DICA: Configure as chaves API no arquivo .env")
        exit(1)