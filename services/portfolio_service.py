# services/portfolio_service.py
from typing import List, Dict, Optional
from data.db_manager import DatabaseManager
from stock_fetcher import get_stock_price
from models.database import Portfolio, Stock


class PortfolioService:
    """Business logic for portfolio management - like C# service layer"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def calculate_stock_value(self, stock: Stock) -> Dict[str, float]:
        """
        Calculate current value and gain/loss for a stock
        
        Returns:
            dict with current_price, current_value, gain_loss, gain_loss_percent
        """
        # Get current price from API
        stock_data = get_stock_price(stock.symbol)
        
        if not stock_data:
            return {
                'symbol': stock.symbol,
                'shares': stock.shares,
                'purchase_price': stock.purchase_price,
                'current_price': 0,
                'current_value': 0,
                'total_cost': stock.total_cost,
                'gain_loss': 0,
                'gain_loss_percent': 0,
                'error': 'Failed to fetch price'
            }
        
        current_price = stock_data['current_price']
        current_value = stock.shares * current_price
        gain_loss = current_value - stock.total_cost
        gain_loss_percent = (gain_loss / stock.total_cost * 100) if stock.total_cost > 0 else 0
        
        return {
            'symbol': stock.symbol,
            'name': stock_data.get('name', stock.symbol),
            'shares': stock.shares,
            'purchase_price': stock.purchase_price,
            'current_price': current_price,
            'total_cost': stock.total_cost,
            'current_value': current_value,
            'gain_loss': gain_loss,
            'gain_loss_percent': gain_loss_percent
        }
    
    def get_portfolio_summary(self, portfolio_id: int) -> Dict:
        """
        Calculate portfolio summary with all stocks
        
        Returns complete portfolio analysis
        """
        portfolio = self.db.get_portfolio(portfolio_id)
        if not portfolio:
            return {'error': 'Portfolio not found'}
        
        stocks = self.db.get_portfolio_stocks(portfolio_id)
        
        if not stocks:
            return {
                'portfolio': portfolio,
                'stocks': [],
                'total_cost': 0,
                'total_value': 0,
                'total_gain_loss': 0,
                'total_gain_loss_percent': 0
            }
        
        # Calculate each stock
        stock_details = []
        total_cost = 0
        total_value = 0
        
        for stock in stocks:
            details = self.calculate_stock_value(stock)
            stock_details.append(details)
            total_cost += details['total_cost']
            total_value += details['current_value']
        
        total_gain_loss = total_value - total_cost
        total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
        
        # Save snapshot for historical tracking
        self.db.save_price_snapshot(portfolio_id, total_value)
        
        return {
            'portfolio': portfolio,
            'stocks': stock_details,
            'total_cost': total_cost,
            'total_value': total_value,
            'total_gain_loss': total_gain_loss,
            'total_gain_loss_percent': total_gain_loss_percent
        }