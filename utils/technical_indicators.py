import pandas as pd
import numpy as np

class TechnicalIndicators:
    @staticmethod
    def calculate_rsi(prices, window=14):
        """Calcula RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """Calcula MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        macd_histogram = macd - macd_signal
        return macd, macd_signal, macd_histogram
    
    def add_all_technical_indicators(self, df, price_column='4. close'):
        """Adiciona todos os indicadores técnicos"""
        prices = df[price_column]
        
        # Retornos
        df['returns'] = prices.pct_change()
        df['log_returns'] = np.log(prices / prices.shift(1))
        
        # Médias móveis
        df['sma_20'] = prices.rolling(20).mean()
        df['sma_50'] = prices.rolling(50).mean()
        df['sma_200'] = prices.rolling(200).mean()
        
        # Volatilidade
        df['volatility_20'] = df['returns'].rolling(20).std()
        
        # Bandas de Bollinger
        df['bb_upper'] = df['sma_20'] + (df['volatility_20'] * 2)
        df['bb_lower'] = df['sma_20'] - (df['volatility_20'] * 2)
        df['bb_position'] = (prices - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # RSI
        df['rsi_14'] = self.calculate_rsi(prices)
        
        # MACD
        df['macd'], df['macd_signal'], df['macd_histogram'] = self.calculate_macd(prices)
        
        return df