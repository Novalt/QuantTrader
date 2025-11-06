# main.py - ARQUIVO PRINCIPAL CORRIGIDO
import pandas as pd
import numpy as np
import sys
import os
import glob
import pickle
from datetime import datetime

# Adicionar diretório raiz ao path para imports absolutos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Agora importar os módulos do projeto
from pipelines.data_collector import DataCollector
from pipelines.data_processor import DataProcessor
from strategies.moving_average import MovingAverageStrategy
from config.settings import settings

def load_latest_collected_data():
    """Carrega os dados coletados mais recentes (arquivos .pkl)"""
    data_files = {}
    for data_type in ['market_data', 'economic_data', 'forex_data']:
        files = glob.glob(f'data/{data_type}_*.pkl')
        if files:
            latest_file = max(files, key=os.path.getctime)
            with open(latest_file, 'rb') as f:
                data_files[data_type] = pickle.load(f)
        else:
            data_files[data_type] = None
    return data_files

def main():
    """Função principal executável"""
    print("🚀 INICIANDO SISTEMA DE TRADING QUANTITATIVO")
    print("=" * 50)
    
    try:
        # 1. COLETAR DADOS
        print("\n📥 1. Coletando dados de mercado...")
        collector = DataCollector()
        collection_success = collector.run_complete_collection()
        
        if not collection_success:
            print("❌ Falha na coleta de dados. Verifique os logs.")
            return False

        # 2. CARREGAR DADOS COLETADOS
        print("\n📂 2. Carregando dados coletados...")
        collected_data = load_latest_collected_data()
        
        if not any(collected_data.values()):
            print("❌ Nenhum dado coletado encontrado.")
            return False

        # 3. PROCESSAR DADOS  
        print("\n🔄 3. Processando dados...")
        processor = DataProcessor()
        processing_success = processor.run_processing(collected_data)
        
        if not processing_success:
            print("❌ Falha no processamento de dados.")
            return False

        # 4. CARREGAR DADOS PROCESSADOS PARA ESTRATÉGIA
        print("\n📊 4. Carregando dados processados...")
        
        # Tenta encontrar um arquivo processado recente
        processed_files = glob.glob('data/processed/*.csv')
        if not processed_files:
            print("❌ Nenhum arquivo processado encontrado.")
            return False

        # Pega o arquivo mais recente
        latest_processed = max(processed_files, key=os.path.getctime)
        df_processed = pd.read_csv(latest_processed, index_col=0, parse_dates=True)
        
        print(f"✅ Dados carregados: {latest_processed} ({len(df_processed)} linhas)")

        # 5. EXECUTAR ESTRATÉGIA
        print("\n🎯 5. Executando estratégia...")
        strategy = MovingAverageStrategy(fast_period=20, slow_period=50)
        signals = strategy.generate_signals(df_processed)
        
        if not signals.empty:
            # 6. EXPORTAR SINAIS
            strategy.export_signals(signals, 'sinais_moving_average.csv')
            print(f"✅ {len(signals)} sinais gerados e exportados")
        else:
            print("⚠️ Nenhum sinal gerado pela estratégia")
        
        print("\n✅ SISTEMA EXECUTADO COM SUCESSO!")
        return True
        
    except Exception as e:
        print(f"❌ ERRO NO SISTEMA: {e}")
        import traceback
        traceback.print_exc()
        return False

def scheduled_execution():
    """Execução agendada do sistema"""
    print(f"\n⏰ Execução agendada: {datetime.now()}")
    success = main()
    
    if success:
        print("✅ Execução agendada concluída")
    else:
        print("❌ Execução agendada falhou")

if __name__ == "__main__":
    # Executar imediatamente
    main()