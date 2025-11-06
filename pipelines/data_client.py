# pipelines/data_client.py - CLIENTE ATUALIZADO
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import numpy as np

# ✅ AGORA ESTE IMPORT DEVE FUNCIONAR
from config.api_endpoints import DataSource, APIEndpoints, APIConfig, MarketSymbols
from config.settings import settings

class ProfessionalDataClient:
    """Cliente profissional para coleta de dados financeiros - ATUALIZADO"""
    
    def __init__(self):
        self.session = requests.Session()
        self.rate_limits = {}
        self.logger = self._setup_logging()
        
        # Configurar headers padrão
        self.session.headers.update({
            'User-Agent': 'QuantTrader/1.0 (Professional Trading System)',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate'
        })
        
    def _setup_logging(self):
        """Configura logging profissional"""
        logging.basicConfig(
            level=settings.LOG_LEVEL,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/data_client.log'),
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
        
        # Reset diário se novo dia
        if now.date() != stats['daily_window']:
            stats['daily_count'] = 0
            stats['daily_window'] = now.date()
            self.logger.info(f"Reset daily counter for {source.value}")
        
        # Reset minuto se novo minuto
        if (now - stats['minute_window']).seconds >= 60:
            stats['minute_count'] = 0
            stats['minute_window'] = now
        
        # Verificar limites
        if stats['minute_count'] >= limits['requests_per_minute']:
            wait_time = 60 - (now - stats['minute_window']).seconds
            self.logger.warning(f"Rate limit minuto excedido para {source.value}. Aguardando {wait_time}s")
            time.sleep(wait_time + 1)
            return self._check_rate_limit(source)  # Recursão após espera
            
        if stats['daily_count'] >= limits['requests_per_day']:
            self.logger.error(f"Rate limit diário excedido para {source.value}")
            return False
        
        stats['minute_count'] += 1
        stats['daily_count'] += 1
        return True
    
    def _make_api_request(self, url: str, params: Dict, source: DataSource) -> Optional[Dict]:
        """Faz requisição API com retry logic robusto"""
        
        for attempt in range(APIConfig.RETRY_CONFIG['max_retries']):
            if not self._check_rate_limit(source):
                return None
                
            try:
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=(
                        APIConfig.TIMEOUT_CONFIG['connect_timeout'],
                        APIConfig.TIMEOUT_CONFIG['read_timeout']
                    )
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Verificar mensagens de erro específicas da API
                if 'Error Message' in data:
                    self.logger.error(f"API Error: {data['Error Message']}")
                    return None
                    
                if 'Information' in data and 'call frequency' in data['Information']:
                    self.logger.warning("Frequência de chamadas da API se aproximando do limite")
                    time.sleep(60)
                    continue
                    
                if 'Note' in data and 'API call frequency' in data['Note']:
                    self.logger.warning("Nota da API: Limite de frequência")
                    time.sleep(60)
                    continue
                    
                return data
                
            except requests.exceptions.Timeout:
                self.logger.error(f"Timeout (attempt {attempt + 1}) para {url}")
                if attempt < APIConfig.RETRY_CONFIG['max_retries'] - 1:
                    sleep_time = APIConfig.RETRY_CONFIG['backoff_factor'] ** attempt
                    time.sleep(sleep_time)
                continue
                
            except requests.exceptions.HTTPError as e:
                self.logger.error(f"HTTP Error {response.status_code} (attempt {attempt + 1}): {e}")
                if response.status_code in APIConfig.RETRY_CONFIG['status_forcelist']:
                    sleep_time = APIConfig.RETRY_CONFIG['backoff_factor'] ** attempt
                    time.sleep(sleep_time)
                    continue
                else:
                    break
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < APIConfig.RETRY_CONFIG['max_retries'] - 1:
                    sleep_time = APIConfig.RETRY_CONFIG['backoff_factor'] ** attempt
                    time.sleep(sleep_time)
                continue
                
        return None
    
    def get_alpha_vantage_data(self, symbol: str, function: str = 'TIME_SERIES_DAILY') -> Optional[pd.DataFrame]:
        """Coleta dados do Alpha Vantage - MELHORADO"""
        
        params = {
            'function': function,
            'symbol': symbol,
            'apikey': settings.ALPHA_VANTAGE_API_KEY,
            'outputsize': 'full',
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
        try:
            if 'Time Series (Daily)' in data:
                time_series = data['Time Series (Daily)']
                df = pd.DataFrame.from_dict(time_series, orient='index')
                
                # Limpar nomes das colunas
                df.columns = [col.split('. ')[1] for col in df.columns]
                df.index = pd.to_datetime(df.index)
                
                # Converter para float
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                df.sort_index(inplace=True)
                self.logger.info(f"Alpha Vantage: {symbol} - {len(df)} registros")
                return df
                
            else:
                self.logger.warning(f"Estrutura inesperada para {symbol}: {list(data.keys())}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro parsing Alpha Vantage {symbol}: {e}")
            return None
    
    def get_forex_data(self, from_currency: str, to_currency: str) -> Optional[pd.DataFrame]:
        """Coleta dados de forex - CORRIGIDO E MELHORADO"""
        
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
        
        if not data:
            return None
            
        try:
            if 'Time Series FX (Daily)' in data:
                time_series = data['Time Series FX (Daily)']
                df = pd.DataFrame.from_dict(time_series, orient='index')
                
                # Limpar nomes das colunas
                df.columns = [col.split('. ')[1] for col in df.columns]
                df.index = pd.to_datetime(df.index)
                
                # Converter para float
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                df.sort_index(inplace=True)
                self.logger.info(f"Forex: {from_currency}{to_currency} - {len(df)} registros")
                return df
                
            else:
                self.logger.warning(f"Estrutura inesperada para forex {from_currency}{to_currency}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro parsing forex {from_currency}{to_currency}: {e}")
            return None

    # ... (mantenha os outros métodos existentes)