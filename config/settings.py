# config/settings.py - CONFIGURAÇÕES QUE LÊEM O .env
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class Settings:
    """Configurações globais do sistema"""
    
    # ==================== APIs EXTERNAS ====================
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    FRED_API_KEY = os.getenv('FRED_API_KEY')
    BRAPI_API_KEY = os.getenv('BRAPI_API_KEY')
    
    # ==================== CONFIGURAÇÕES DE MERCADO ====================
    @property
    def ASSETS_CONFIG(self) -> Dict:
        return {
            'stocks': os.getenv('STOCKS_BR', 'BOVA11.SAO').split(','),
            'forex': os.getenv('FOREX_PAIRS', 'USDBRL').split(','),
            'commodities': os.getenv('COMMODITIES', 'GC=F').split(','),
            'di1_contracts': os.getenv('DI1_CONTRACTS', 'DI1F26,DI1F28').split(',')
        }
    
    # ==================== PARÂMETROS DE RISCO ====================
    RISK_PER_TRADE = float(os.getenv('RISK_PER_TRADE', 0.02))
    MAX_DRAWDOWN = float(os.getenv('MAX_DRAWDOWN', 0.15))
    MAX_POSITION_SIZE = int(os.getenv('MAX_POSITION_SIZE', 10))
    
    # Stops e Takes padrão
    STOP_LOSS_WIN = int(os.getenv('DEFAULT_STOP_LOSS_WIN', 250))
    TAKE_PROFIT_WIN = int(os.getenv('DEFAULT_TAKE_PROFIT_WIN', 550))
    STOP_LOSS_WDO = int(os.getenv('DEFAULT_STOP_LOSS_WDO', 100))
    TAKE_PROFIT_WDO = int(os.getenv('DEFAULT_TAKE_PROFIT_WDO', 250))
    
    # ==================== CONFIGURAÇÕES DO SISTEMA ====================
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_LAKE_PATH = os.getenv('DATA_LAKE_PATH', './data_lake')
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', 30))
    
    # ==================== AGENDAMENTO ====================
    DATA_COLLECTION_TIME = os.getenv('DATA_COLLECTION_TIME', '18:00')
    MACRO_UPDATE_DAY = os.getenv('MACRO_UPDATE_DAY', 'monday')
    MACRO_UPDATE_TIME = os.getenv('MACRO_UPDATE_TIME', '09:00')
    
    # ==================== PERFORMANCE ====================
    MAX_API_RETRIES = int(os.getenv('MAX_API_RETRIES', 3))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
    BACKOFF_FACTOR = int(os.getenv('BACKOFF_FACTOR', 2))
    
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_EXPIRY_HOURS = int(os.getenv('CACHE_EXPIRY_HOURS', 24))
    
    # ==================== E-MAIL (OPCIONAL) ====================
    EMAIL_ALERTS_ENABLED = os.getenv('EMAIL_ALERTS_ENABLED', 'false').lower() == 'true'
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    EMAIL_TO = os.getenv('EMAIL_TO')
    
    # ==================== DATA DE INÍCIO PADRÃO ====================
    START_DATE = os.getenv('START_DATE', '2000-01-01')
    
    # ==================== VALIDAÇÃO ====================
    def validate_settings(self):
        """Valida configurações essenciais"""
        errors = []
        
        if not self.ALPHA_VANTAGE_API_KEY:
            errors.append("ALPHA_VANTAGE_API_KEY não configurada")
        
        if not self.FRED_API_KEY:
            errors.append("FRED_API_KEY não configurada")
        
        if self.RISK_PER_TRADE > 0.05:
            errors.append("RISK_PER_TRADE muito alto (max 0.05)")
        
        if errors:
            raise ValueError(f"Erros de configuração: {', '.join(errors)}")
        
        return True

# Instância global das configurações
settings = Settings()

# Validação automática ao importar
try:
    settings.validate_settings()
    print("✅ Configurações validadas com sucesso!")
except ValueError as e:
    print(f"❌ Erro nas configurações: {e}")