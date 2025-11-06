# pipelines/data_processor.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
import os

class DataProcessor:
    """Processador de dados para análise quantitativa"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
    def process_collected_data(self, collected_data: Dict) -> Dict[str, pd.DataFrame]:
        """
        Processa os dados coletados pelo DataCollector
        """
        processed_data = {}
        
        try:
            # Processa dados de mercado
            if 'market_data' in collected_data:
                market_data = collected_data['market_data']
                for symbol, df in market_data.items():
                    if symbol.endswith(('_SMA_50', '_RSI_14')):
                        # Já são indicadores técnicos, apenas renomeia
                        processed_data[symbol] = df
                    else:
                        # Processa dados de preço
                        processed_df = self._process_price_data(df, symbol)
                        processed_data[symbol] = processed_df
            
            # Processa dados econômicos
            if 'economic_data' in collected_data:
                economic_data = collected_data['economic_data']
                for series_id, df in economic_data.items():
                    processed_df = self._process_economic_data(df, series_id)
                    processed_data[series_id] = processed_df
            
            # Processa dados forex
            if 'forex_data' in collected_data:
                forex_data = collected_data['forex_data']
                for pair, df in forex_data.items():
                    processed_df = self._process_forex_data(df, pair)
                    processed_data[pair] = processed_df
                    
            self.logger.info(f"PROCESSADOS {len(processed_data)} DATASETS")
            
        except Exception as e:
            self.logger.error(f"ERRO NO PROCESSAMENTO: {e}")
            
        return processed_data
    
    def _process_price_data(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Processa dados de preço de ações"""
        try:
            # Garante que todas as colunas necessárias existem
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            
            # Renomeia colunas se necessário
            if len(df.columns) >= 4:
                df.columns = ['open', 'high', 'low', 'close', 'volume'][:len(df.columns)]
            
            # Calcula retornos
            df['returns'] = df['close'].pct_change()
            
            # Calcula volatilidade
            df['volatility'] = df['returns'].rolling(window=20).std()
            
            # Médias móveis
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            
            # RSI
            df['rsi_14'] = self._calculate_rsi(df['close'])
            
            # MACD
            macd, signal = self._calculate_macd(df['close'])
            df['macd'] = macd
            df['macd_signal'] = signal
            
            df.dropna(inplace=True)
            return df
            
        except Exception as e:
            self.logger.error(f"ERRO AO PROCESSAR {symbol}: {e}")
            return df
    
    def _process_economic_data(self, df: pd.DataFrame, series_id: str) -> pd.DataFrame:
        """Processa dados econômicos do FRED"""
        try:
            # Remove valores NaN
            df.dropna(inplace=True)
            
            # Calcula variação percentual
            if len(df) > 1:
                df['pct_change'] = df[series_id].pct_change()
                
            return df
        except Exception as e:
            self.logger.error(f"ERRO AO PROCESSAR SERIE {series_id}: {e}")
            return df
    
    def _process_forex_data(self, df: pd.DataFrame, pair: str) -> pd.DataFrame:
        """Processa dados de forex"""
        try:
            # Renomeia colunas se necessário
            if len(df.columns) >= 2:
                df.columns = ['open', 'high', 'low', 'close'][:len(df.columns)]
            
            # Calcula retornos
            df['returns'] = df['close'].pct_change()
            
            # Médias móveis
            df['sma_20'] = df['close'].rolling(window=20).mean()
            
            df.dropna(inplace=True)
            return df
            
        except Exception as e:
            self.logger.error(f"ERRO AO PROCESSAR FOREX {pair}: {e}")
            return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcula RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series) -> tuple:
        """Calcula MACD"""
        exp1 = prices.ewm(span=12).mean()
        exp2 = prices.ewm(span=26).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()
        return macd, signal

    def run_processing(self, collected_data: Dict) -> bool:
        """
        Executa o processamento completo
        """
        try:
            self.logger.info("INICIANDO PROCESSAMENTO DE DADOS...")
            
            processed_data = self.process_collected_data(collected_data)
            
            if processed_data:
                # Salva dados processados
                self._save_processed_data(processed_data)
                self.logger.info(f"PROCESSAMENTO CONCLUIDO: {len(processed_data)} DATASETS")
                return True
            else:
                self.logger.warning("NENHUM DADO PROCESSADO")
                return False
                
        except Exception as e:
            self.logger.error(f"ERRO NO PROCESSAMENTO: {e}")
            return False
    
    def _save_processed_data(self, processed_data: Dict[str, pd.DataFrame]):
        """Salva dados processados"""
        try:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs('data/processed', exist_ok=True)
            
            for name, df in processed_data.items():
                filename = f"data/processed/{name}_{timestamp}.csv"
                df.to_csv(filename)
                self.logger.info(f"DADOS PROCESSADOS SALVOS: {filename}")
                
        except Exception as e:
            self.logger.error(f"ERRO AO SALVAR DADOS PROCESSADOS: {e}")