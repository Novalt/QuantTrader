# Package initialization
# strategies/__init__.py - TORNAR strategies UM PACOTE
from .base_strategy import BaseStrategy
from .moving_average import MovingAverageStrategy

__all__ = ['BaseStrategy', 'MovingAverageStrategy']