# strategies/base_strategy.py - CLASSE BASE CORRIGIDA
from abc import ABC, abstractmethod
import pandas as pd
import os
import sys

# Adicionar o diretório raiz ao path para imports absolutos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

class BaseStrategy(ABC):
    """
    Classe base abstrata para todas as estratégias de trading
    Implementa métodos comuns e interface padrão
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.data_path = settings.DATA_LAKE_PATH
        self.signals_generated = 0
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Método abstrato - deve ser implementado por todas as estratégias
        Retorna DataFrame com sinais de trading
        """
        pass
    
    def calculate_performance(self, signals_df: pd.DataFrame) -> dict:
        """Calcula métricas de performance básicas"""
        if signals_df.empty:
            return {}
            
        performance = {
            'total_signals': len(signals_df),
            'buy_signals': len(signals_df[signals_df['signal'] > 0]),
            'sell_signals': len(signals_df[signals_df['signal'] < 0]),
            'neutral_signals': len(signals_df[signals_df['signal'] == 0]),
            'strategy_name': self.name
        }
        
        # Adicionar métricas de retorno se disponíveis
        if 'returns' in signals_df.columns:
            performance['total_return'] = signals_df['returns'].sum()
            performance['win_rate'] = (signals_df['returns'] > 0).mean()
            
        return performance
    
    def export_signals(self, signals_df: pd.DataFrame, filename: str = None) -> str:
        """Exporta sinais para CSV"""
        if filename is None:
            filename = f"{self.name}_signals.csv"
            
        output_path = f"{self.data_path}/processed/signals/{filename}"
        
        try:
            signals_df.to_csv(output_path, index=False)
            self.signals_generated = len(signals_df)
            print(f"✅ Sinais exportados: {output_path} ({len(signals_df)} sinais)")
            return output_path
        except Exception as e:
            print(f"❌ Erro exportando sinais: {e}")
            return ""
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Valida dados de entrada"""
        required_columns = ['open', 'high', 'low', 'close']
        
        if data.empty:
            print("❌ Dados vazios")
            return False
            
        for col in required_columns:
            if col not in data.columns:
                print(f"❌ Coluna obrigatória faltando: {col}")
                return False
                
        return True
    
    def __str__(self):
        return f"Estratégia: {self.name} - {self.description}"
    
    def __repr__(self):
        return f"BaseStrategy(name='{self.name}', signals_generated={self.signals_generated})"