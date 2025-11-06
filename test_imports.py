# test_imports.py - TESTAR TODOS OS IMPORTS
import sys
import os

def test_all_imports():
    """Testa todos os imports do projeto"""
    print("🧪 TESTANDO IMPORTS DO PROJETO")
    print("=" * 40)
    
    # Adicionar diretório raiz
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    tests = [
        ("config.settings", "settings"),
        ("strategies.base_strategy", "BaseStrategy"),
        ("strategies.moving_average", "MovingAverageStrategy"), 
        ("pipelines.data_collector", "DataCollector"),
        ("pipelines.data_processor", "DataProcessor"),
    ]
    
    all_passed = True
    
    for module_name, class_name in tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {module_name}.{class_name} - OK")
        except ImportError as e:
            print(f"❌ {module_name}.{class_name} - FALHA: {e}")
            all_passed = False
        except AttributeError as e:
            print(f"❌ {module_name}.{class_name} - FALHA: {e}")
            all_passed = False
    
    print("=" * 40)
    if all_passed:
        print("🎉 TODOS OS IMPORTS FUNCIONANDO!")
    else:
        print("💡 ALGUNS IMPORTS PRECISAM DE AJUSTE")
    
    return all_passed

if __name__ == "__main__":
    test_all_imports()