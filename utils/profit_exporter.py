import pandas as pd
from datetime import datetime

class ProfitExporter:
    def __init__(self):
        self.profit_columns = ['Symbol', 'Action', 'Price', 'Strength', 'Timestamp']
    
    def format_signals(self, signals_df, symbol):
        """Formata os sinais para o formato do Profit Pro"""
        formatted_signals = []
        
        for index, row in signals_df.iterrows():
            action = 'BUY' if row['entry'] == 1 else 'SELL'
            signal = {
                'Symbol': symbol,
                'Action': action,
                'Price': row['4. close'],
                'Strength': row['strength'],
                'Timestamp': index.strftime('%Y-%m-%d %H:%M:%S')
            }
            formatted_signals.append(signal)
        
        return pd.DataFrame(formatted_signals)
    
    def export_to_csv(self, signals_df, symbol, filename=None):
        """Exporta os sinais para CSV"""
        if filename is None:
            filename = f"profit_signals_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        formatted_df = self.format_signals(signals_df, symbol)
        file_path = f"data_lake/processed/signals/{filename}"
        formatted_df.to_csv(file_path, index=False)
        print(f"✓ Sinais exportados para {file_path}")
        return file_path