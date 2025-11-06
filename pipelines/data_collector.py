# pipelines/data_collector.py - CLIENTE DE DADOS ROBUSTO
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import logging
from config.api_endpoints import DataSource, APIEndpoints, APIConfig
from config.settings import settings

class ProfessionalDataClient:
    """Cliente profissional para coleta de dados financeiros"""
    
    def __init__(self):
        self.session = requests.Session()
        self.rate_limits = {}
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """Configura logging profissional"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/data_pipeline.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _check_rate_limit(self, source: DataSource) -> bool:
        """Verifica e controla rate limits"""
        now = datetime.now()
        source_key = source.value
        
        if source_key not in self.rate_limits:
            self.rate_limits[source_key] = {
                'minute_count': 0,
                'minute_window': now,
                'daily_count': 0,
                'daily_window': now.date()
            }
        
        limits = APIConfig.RATE_LIMITS[source]
        stats = self.rate_limits[source_key]
        
        # Reset daily counter if new day
        if now.date() != stats['daily_window']:
            stats['daily_count'] = 0
            stats['daily_window'] = now.date()
        
        # Reset minute counter if new minute
        if (now - stats['minute_window']).seconds >= 60:
            stats['minute_count'] = 0
            stats['minute_window'] = now
        
        # Check limits
        if (stats['minute_count'] >= limits['requests_per_minute'] or 
            stats['daily_count'] >= limits['requests_per_day']):
            self.logger.warning(f"Rate limit exceeded for {source.value}")
            return False
        
        stats['minute_count'] += 1
        stats['daily_count'] += 1
        return True
    
    def _make_api_request(self, url: str, params: Dict, source: DataSource, max_retries: int = 3) -> Optional[Dict]:
        """Faz requisição API com retry logic"""
        
        for attempt in range(max_retries):
            if not self._check_rate_limit(source):
                time.sleep(60)  # Wait a minute if rate limited
                continue
                
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # Check for API-specific error messages
                if 'Error Message' in data:
                    self.logger.error(f"API Error: {data['Error Message']}")
                    return None
                if 'Information' in data and 'call frequency' in data['Information']:
                    self.logger.warning("API call frequency limit approaching")
                    time.sleep(60)
                    continue
                    
                return data
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    sleep_time = APIConfig.RETRY_CONFIG['backoff_factor'] ** attempt
                    time.sleep(sleep_time)
                continue
                
        return None
    
    def get_alpha_vantage_data(self, symbol: str, function: str = 'TIME_SERIES_DAILY', 
                             output_size: str = 'full') -> Optional[pd.DataFrame]:
        """Coleta dados do Alpha Vantage"""
        
        params = {
            'function': function,
            'symbol': symbol,
            'apikey': settings.ALPHA_VANTAGE_API_KEY,
            'outputsize': output_size,
            'datatype': 'json'
        }
        
        data = self._make_api_request(
            APIEndpoints.ALPHA_VANTAGE_BASE, 
            params, 
            DataSource.ALPHA_VANTAGE
        )
        
        if not data:
            return None
            
        # Parse Alpha Vantage response
        if 'Time Series (Daily)' in data:
            df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
            df.columns = [col.split(' ')[1] for col in df.columns]  # Clean column names
            df.index = pd.to_datetime(df.index)
            df = df.astype(float)
            df.sort_index(inplace=True)
            return df
            
        return None
    
    def get_fred_data(self, series_id: str, start_date: str = '2000-01-01') -> Optional[pd.DataFrame]:
        """Coleta dados do FRED"""
        
        params = {
            'series_id': series_id,
            'api_key': settings.FRED_API_KEY,
            'file_type': 'json',
            'observation_start': start_date
        }
        
        url = f"{APIEndpoints.FRED_BASE}/series/observations"
        data = self._make_api_request(url, params, DataSource.FRED)
        
        if not data or 'observations' not in data:
            return None
            
        df = pd.DataFrame(data['observations'])
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df.set_index('date', inplace=True)
        df = df[['value']]
        df.columns = [series_id]
        
        return df
    
    def get_technical_indicators(self, symbol: str, indicator: str, 
                               time_period: int = 50, series_type: str = 'close') -> Optional[pd.DataFrame]:
        """Obtém indicadores técnicos do Alpha Vantage"""
        
        params = {
            'function': indicator,
            'symbol': symbol,
            'interval': 'daily',
            'time_period': time_period,
            'series_type': series_type,
            'apikey': settings.ALPHA_VANTAGE_API_KEY
        }
        
        data = self._make_api_request(
            APIEndpoints.ALPHA_VANTAGE_BASE,
            params,
            DataSource.ALPHA_VANTAGE
        )
        
        if not data or f'Technical Analysis: {indicator}' not in data:
            return None
            
        tech_data = data[f'Technical Analysis: {indicator}']
        df = pd.DataFrame.from_dict(tech_data, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)
        df.sort_index(inplace=True)
        
        return df
    
    def get_forex_data(self, from_currency: str, to_currency: str) -> Optional[pd.DataFrame]:
        """Coleta dados de forex"""
        params = {
            'function': 'FX_DAILY',
            'from_symbol': from_currency,
            'to_symbol': to_currency,
            'apikey': settings.ALPHA_VANTAGE_API_KEY,
            'outputsize': 'full'
        }
        
        data = self._make_api_request(
            APIEndpoints.ALPHA_VANTAGE_BASE,
            params,
            DataSource.ALPHA_VANTAGE
        )
        
        if not data or 'Time Series FX (Daily)' not in data:
            return None
            
        df = pd.DataFrame.from_dict(data['Time Series FX (Daily)'], orient='index')
        df.columns = [col.split(' ')[1] for col in df.columns]
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)
        df.sort_index(inplace=True)
        
        return df

class DataCollector:
    """
    Coletor de dados principal que encapsula o ProfessionalDataClient
    e fornece interface padronizada para o pipeline
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.client = ProfessionalDataClient()
        self.logger = logging.getLogger(__name__)
        
    def run_complete_collection(self) -> bool:
        """
        Executa a coleta completa de dados conforme configurado
        Retorna True se bem-sucedido, False caso contrário
        """
        try:
            self.logger.info("INICIANDO COLETA COMPLETA DE DADOS...")
            
            # Configurações padrão
            symbols = self.config.get('symbols', ['AAPL', 'MSFT', 'GOOGL'])
            economic_series = self.config.get('economic_series', ['GDP', 'CPIAUCSL', 'UNRATE'])
            forex_pairs = self.config.get('forex_pairs', [('USD', 'BRL'), ('EUR', 'USD')])
            start_date = self.config.get('start_date', '2020-01-01')
            end_date = self.config.get('end_date', datetime.now().strftime('%Y-%m-%d'))
            
            self.logger.info(f"COLETANDO DADOS DE {len(symbols)} SIMBOLOS")
            self.logger.info(f"COLETANDO {len(economic_series)} SERIES ECONOMICAS")
            self.logger.info(f"COLETANDO {len(forex_pairs)} PARES FOREX")
            
            # Coleta dados de mercado
            market_data = self.collect_market_data(symbols, start_date, end_date)
            economic_data = self.collect_economic_data(economic_series, start_date)
            forex_data = self.collect_forex_data(forex_pairs, start_date, end_date)
            
            # Verifica se a coleta foi bem-sucedida
            success = bool(market_data or economic_data or forex_data)
            
            if success:
                self.logger.info("COLETA COMPLETA FINALIZADA COM SUCESSO!")
                # Salva os dados coletados (opcional)
                self._save_collected_data({
                    'market_data': market_data,
                    'economic_data': economic_data,
                    'forex_data': forex_data
                })
            else:
                self.logger.warning("COLETA COMPLETADA MAS NENHUM DADO FOI OBTIDO")
                
            return success
            
        except Exception as e:
            self.logger.error(f"ERRO NA COLETA COMPLETA: {e}")
            return False
    
    def _save_collected_data(self, data_dict: Dict):
        """
        Salva os dados coletados em arquivos (opcional)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for data_type, data in data_dict.items():
                if data:
                    filename = f"data/{data_type}_{timestamp}.pkl"
                    # Cria diretório se não existir
                    import os
                    os.makedirs('data', exist_ok=True)
                    
                    import pickle
                    with open(filename, 'wb') as f:
                        pickle.dump(data, f)
                    
                    # REMOVIDO EMOJI
                    self.logger.info(f"Dados {data_type} salvos em {filename}")
                    
        except Exception as e:
            self.logger.warning(f"Nao foi possivel salvar dados: {e}")

    # MANTENHA OS OUTROS MÉTODOS QUE JÁ EXISTIAM (collect_market_data, collect_economic_data, etc.)
    def collect_market_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """
        Coleta dados de mercado para múltiplos símbolos
        """
        data = {}
        
        for symbol in symbols:
            self.logger.info(f"Coletando dados para {symbol}")
            
            # Coleta dados de preço
            price_data = self.client.get_alpha_vantage_data(
                symbol=symbol,
                function='TIME_SERIES_DAILY',
                output_size='full'
            )
            
            if price_data is not None:
                # Filtra pelo período desejado
                price_data = price_data.loc[start_date:end_date]
                data[symbol] = price_data
                
                # Coleta indicadores técnicos
                try:
                    # SMA 50
                    sma_50 = self.client.get_technical_indicators(
                        symbol=symbol, 
                        indicator='SMA', 
                        time_period=50
                    )
                    if sma_50 is not None:
                        data[f"{symbol}_SMA_50"] = sma_50.loc[start_date:end_date]
                    
                    # RSI 14
                    rsi_14 = self.client.get_technical_indicators(
                        symbol=symbol, 
                        indicator='RSI', 
                        time_period=14
                    )
                    if rsi_14 is not None:
                        data[f"{symbol}_RSI_14"] = rsi_14.loc[start_date:end_date]
                        
                except Exception as e:
                    self.logger.warning(f"Erro ao coletar indicadores para {symbol}: {e}")
            else:
                self.logger.warning(f"Falha ao coletar dados para {symbol}")
                
            # Respeita rate limits
            time.sleep(12)  # Alpha Vantage free tier: 5 requests/minuto
        
        return data
    
    def collect_economic_data(self, series_ids: List[str], start_date: str) -> Dict[str, pd.DataFrame]:
        """
        Coleta dados econômicos do FRED
        """
        data = {}
        
        for series_id in series_ids:
            self.logger.info(f"Coletando série econômica: {series_id}")
            
            fred_data = self.client.get_fred_data(
                series_id=series_id,
                start_date=start_date
            )
            
            if fred_data is not None:
                data[series_id] = fred_data
            else:
                self.logger.warning(f"Falha ao coletar série FRED: {series_id}")
        
        return data
    
    def collect_forex_data(self, currency_pairs: List[tuple], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """
        Coleta dados de forex
        """
        data = {}
        
        for from_curr, to_curr in currency_pairs:
            pair_name = f"{from_curr}{to_curr}"
            self.logger.info(f"Coletando dados forex: {pair_name}")
            
            forex_data = self.client.get_forex_data(
                from_currency=from_curr,
                to_currency=to_curr
            )
            
            if forex_data is not None:
                forex_data = forex_data.loc[start_date:end_date]
                data[pair_name] = forex_data
            else:
                self.logger.warning(f"Falha ao coletar forex: {pair_name}")
            
            # Respeita rate limits
            time.sleep(12)
        
        return data
    
    def collect_economic_data(self, series_ids: List[str], start_date: str) -> Dict[str, pd.DataFrame]:
        """
        Coleta dados econômicos do FRED
        """
        data = {}
        
        for series_id in series_ids:
            self.logger.info(f"Coletando série econômica: {series_id}")
            
            fred_data = self.client.get_fred_data(
                series_id=series_id,
                start_date=start_date
            )
            
            if fred_data is not None:
                data[series_id] = fred_data
            else:
                self.logger.warning(f"Falha ao coletar série FRED: {series_id}")
        
        return data
    
    def collect_forex_data(self, currency_pairs: List[tuple], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """
        Coleta dados de forex
        """
        data = {}
        
        for from_curr, to_curr in currency_pairs:
            pair_name = f"{from_curr}{to_curr}"
            self.logger.info(f"Coletando dados forex: {pair_name}")
            
            forex_data = self.client.get_forex_data(
                from_currency=from_curr,
                to_currency=to_curr
            )
            
            if forex_data is not None:
                forex_data = forex_data.loc[start_date:end_date]
                data[pair_name] = forex_data
            else:
                self.logger.warning(f"Falha ao coletar forex: {pair_name}")
            
            # Respeita rate limits
            time.sleep(12)
        
        return data

# Adicione esta linha para facilitar o import
__all__ = ['DataCollector', 'ProfessionalDataClient']