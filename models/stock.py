# models/stock.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Stock:
    """Represents a stock holding"""
    id: int = None
    symbol: str = ""
    shares: float = 0
    purchase_price: float = 0
    purchase_date: datetime = None
    portfolio_id: int = None
    
    @property
    def total_cost(self):
        """Calculate total cost of this holding"""
        return self.shares * self.purchase_price


@dataclass
class Portfolio:
    """Represents a portfolio of stocks"""
    id: int = None
    name: str = ""
    description: str = ""
    created_date: datetime = None