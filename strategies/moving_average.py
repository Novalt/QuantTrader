# strategies/moving_average.py - ESTRATÉGIA MÉDIA MÓVEL CORRIGIDA
import pandas as pd
import numpy as np
import os
import sys

# Adicionar path para imports absolutos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.base_strategy import BaseStrategy

class MovingAverageStrategy(BaseStrategy):
    """
    Estratégia de Crossover de Médias Móveis
    Compra quando média rápida cruza acima da lenta
    Vende quando média rápida cruza abaixo da lenta
    """
    
    def __init__(self, fast_period: int = 20, slow_period: int = 50):
        super().__init__(
            name="MovingAverageCrossover",
            description=f"Crossover de MMs {fast_period}/{slow_period}"
        )
        self.fast_period = fast_period
        self.slow_period = slow_period
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Gera sinais baseados em crossover de médias móveis
        
        Args:
            data: DataFrame com colunas ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            
        Returns:
            DataFrame com sinais: 1 (COMPRA), -1 (VENDA), 0 (NEUTRO)
        """
        
        # Validar dados
        if not self.validate_data(data):
            return pd.DataFrame()
        
        # Criar cópia para não modificar original
        df = data.copy()
        
        # Calcular médias móveis
        df['fast_ma'] = df['close'].rolling(window=self.fast_period).mean()
        df['slow_ma'] = df['close'].rolling(window=self.slow_period).mean()
        
        # Gerar sinais
        df['signal'] = 0  # Neutro por padrão
        
        # Compra: MM rápida cruza acima da lenta
        buy_condition = (
            (df['fast_ma'] > df['slow_ma']) & 
            (df['fast_ma'].shift(1) <= df['slow_ma'].shift(1))
        )
        
        # Venda: MM rápida cruza abaixo da lenta  
        sell_condition = (
            (df['fast_ma'] < df['slow_ma']) & 
            (df['fast_ma'].shift(1) >= df['slow_ma'].shift(1))
        )
        
        df.loc[buy_condition, 'signal'] = 1    # COMPRA
        df.loc[sell_condition, 'signal'] = -1  # VENDA
        
        # Adicionar metadados
        df['strategy'] = self.name
        df['timestamp'] = pd.Timestamp.now()
        
        # Filtrar apenas linhas com sinais
        signals_df = df[df['signal'] != 0].copy()
        
        if not signals_df.empty:
            print(f"✅ {self.name}: {len(signals_df)} sinais gerados")
            
            # Calcular performance
            performance = self.calculate_performance(signals_df)
            print(f"📊 Performance: {performance}")
            
        return signals_df
    
    def optimize_parameters(self, data: pd.DataFrame, fast_range: range = range(10, 30), 
                          slow_range: range = range(40, 60)) -> dict:
        """
        Otimiza períodos das médias móveis
        """
        best_result = {'sharpe': -np.inf}
        
        for fast in fast_range:
            for slow in slow_range:
                if fast >= slow:
                    continue
                    
                self.fast_period = fast
                self.slow_period = slow
                
                signals = self.generate_signals(data)
                
                if len(signals) > 5:  # Mínimo de sinais
                    # Calcular Sharpe ratio simples (apenas exemplo)
                    sharpe = len(signals) / (slow - fast)
                    
                    if sharpe > best_result['sharpe']:
                        best_result = {
                            'sharpe': sharpe,
                            'fast_period': fast,
                            'slow_period': slow,
                            'signals_count': len(signals)
                        }
        
        # Aplicar melhores parâmetros
        self.fast_period = best_result['fast_period']
        self.slow_period = best_result['slow_period']
        
        print(f"🎯 Melhores parâmetros: {best_result}")
        return best_result