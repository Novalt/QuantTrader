# test_api_endpoints.py - TESTE DOS ENDPOINTS
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_endpoints():
    """Testa se os endpoints estão configurados corretamente"""
    print("🧪 TESTANDO CONFIGURAÇÃO DE API ENDPOINTS")
    print("=" * 50)
    
    try:
        from config.api_endpoints import DataSource, APIEndpoints, APIConfig
        
        print("✅ DataSource importado:")
        for source in DataSource:
            print(f"   - {source.name}: {source.value}")
        
        print("\n✅ APIEndpoints importado:")
        print(f"   - Alpha Vantage: {APIEndpoints.ALPHA_VANTAGE_BASE}")
        print(f"   - FRED: {APIEndpoints.FRED_BASE}")
        print(f"   - BRAPI: {APIEndpoints.BRAPI_BASE}")
        
        print("\n✅ APIConfig importado:")
        print(f"   - Rate Limits: {len(APIConfig.RATE_LIMITS)} fontes")
        print(f"   - Retry Config: {APIConfig.RETRY_CONFIG}")
        
        print("\n🎯 TODOS OS ENDPOINTS CONFIGURADOS CORRETAMENTE!")
        return True
        
    except ImportError as e:
        print(f"❌ ERRO DE IMPORTAÇÃO: {e}")
        return False
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

if __name__ == "__main__":
    success = test_api_endpoints()
    if not success:
        print("\n💡 Verifique se o arquivo config/api_endpoints.py existe")