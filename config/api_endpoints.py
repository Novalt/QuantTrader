# config/api_endpoints.py - ENDPOINTS DE API PROFISSIONAIS
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Any

class DataSource(Enum):
    """Fontes de dados disponíveis"""
    ALPHA_VANTAGE = "alpha_vantage"
    FRED = "fred"
    YAHOO_FINANCE = "yahoo"
    BRAPI = "brapi"
    B3 = "b3"
    MANUAL = "manual"

class APIEndpoints:
    """Configurações de endpoints para todas as APIs"""
    
    # Alpha Vantage
    ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"
    ALPHA_VANTAGE_FUNCTIONS = {
        'TIME_SERIES_DAILY': 'TIME_SERIES_DAILY',
        'TIME_SERIES_INTRADAY': 'TIME_SERIES_INTRADAY',
        'FX_DAILY': 'FX_DAILY',
        'FX_INTRADAY': 'FX_INTRADAY',
        'SMA': 'SMA',
        'EMA': 'EMA',
        'RSI': 'RSI',
        'MACD': 'MACD',
        'BBANDS': 'BBANDS',
        'STOCH': 'STOCH'
    }
    
    # FRED (Federal Reserve Economic Data)
    FRED_BASE = "https://api.stlouisfed.org/fred"
    FRED_ENDPOINTS = {
        'SERIES': '/series/observations',
        'SERIES_INFO': '/series',
        'CATEGORY': '/category/series',
        'RELEASES': '/releases'
    }
    
    # BRAPI (Dados Brasileiros)
    BRAPI_BASE = "https://brapi.dev/api"
    BRAPI_ENDPOINTS = {
        'QUOTE': '/quote/',
        'HISTORICAL': '/quote/{ticker}/historical',
        'DIVIDENDS': '/quote/{ticker}/dividends',
        'CRYPTO': '/v2/crypto'
    }
    
    # Yahoo Finance (Fallback)
    YAHOO_BASE = "https://query1.finance.yahoo.com/v8/finance/chart/"
    
    # B3 (Bolsa Brasil - Dados Públicos)
    B3_ENDPOINTS = {
        'COTACOES_HISTORICAS': 'http://bvmf.bmfbovespa.com.br/InstDados/SerHist/',
        'DERIVATIVES': 'http://www2.bmf.com.br/pages/portal/bmfbovespa/boletim1/'
    }

class APIConfig:
    """Configurações de rate limiting, retry e timeouts"""
    
    # Rate Limits por fonte (requests por minuto)
    RATE_LIMITS = {
        DataSource.ALPHA_VANTAGE: {
            'requests_per_minute': 5,
            'requests_per_day': 500,
            'free_tier': True
        },
        DataSource.FRED: {
            'requests_per_minute': 10,
            'requests_per_day': 1000,
            'free_tier': True
        },
        DataSource.BRAPI: {
            'requests_per_minute': 5,
            'requests_per_day': 100,
            'free_tier': True
        },
        DataSource.YAHOO_FINANCE: {
            'requests_per_minute': 20,
            'requests_per_day': 2000,
            'free_tier': True
        }
    }
    
    # Configurações de Retry
    RETRY_CONFIG = {
        'max_retries': 3,
        'backoff_factor': 2,
        'status_forcelist': [429, 500, 502, 503, 504],
        'allowed_methods': ['GET', 'POST'],
        'respect_retry_after_header': True
    }
    
    # Timeouts
    TIMEOUT_CONFIG = {
        'connect_timeout': 10,
        'read_timeout': 30,
        'total_timeout': 60
    }

class MarketSymbols:
    """Símbolos padronizados para diferentes mercados"""
    
    # Ações Brasileiras
    STOCKS_BR = {
        'BOVA11': 'BOVA11.SAO',  # ETF Ibovespa
        'ITSA4': 'ITSA4.SAO',
        'PETR4': 'PETR4.SAO',
        'VALE3': 'VALE3.SAO',
        'BBDC4': 'BBDC4.SAO',
        'WEGE3': 'WEGE3.SAO',
        'MGLU3': 'MGLU3.SAO'
    }
    
    # Forex (Moedas)
    FOREX_PAIRS = {
        'USDBRL': ('USD', 'BRL'),
        'EURBRL': ('EUR', 'BRL'),
        'BRLJPY': ('BRL', 'JPY'),
        'EURUSD': ('EUR', 'USD'),
        'GBPUSD': ('GBP', 'USD')
    }
    
    # Commodities
    COMMODITIES = {
        'GOLD': 'GC=F',
        'SILVER': 'SI=F',
        'OIL': 'CL=F',
        'COPPER': 'HG=F',
        'SOYBEANS': 'ZS=F'
    }
    
    # Índices Globais
    INDICES = {
        'SP500': '^GSPC',
        'DOWJONES': '^DJI',
        'NASDAQ': '^IXIC',
        'FTSE100': '^FTSE',
        'DAX': '^GDAXI'
    }

class DataValidation:
    """Configurações para validação de dados"""
    
    # Requisitos mínimos de qualidade
    MIN_DATA_POINTS = {
        'daily': 100,
        'hourly': 1000,
        'minute': 10000
    }
    
    # Colunas obrigatórias por tipo de dado
    REQUIRED_COLUMNS = {
        'stock_daily': ['open', 'high', 'low', 'close', 'volume'],
        'forex_daily': ['open', 'high', 'low', 'close'],
        'economic': ['value', 'date']
    }
    
    # Limites para detecção de outliers
    OUTLIER_THRESHOLDS = {
        'price_change_daily': 0.25,  # 25%
        'volume_spike': 5.0,         # 500% do normal
        'missing_data': 0.1          # Máx 10% dados faltantes
    }

def get_default_parameters() -> Dict[str, Any]:
    """Retorna parâmetros padrão para APIs"""
    return {
        'outputsize': 'full',
        'datatype': 'json',
        'interval': 'daily',
        'time_period': 50,
        'series_type': 'close'
    }