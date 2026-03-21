# data/db_manager.py
from typing import List, Optional
from sqlalchemy.orm import Session
from models.database import Portfolio, Stock, PriceHistory, SessionLocal, init_db
from datetime import datetime


class DatabaseManager:
    """Manages database operations - like your C# controllers!"""
    
    def __init__(self):
        """Initialize database"""
        init_db()
    
    def get_session(self) -> Session:
        """Get new database session"""
        return SessionLocal()
    
    # ============================================
    # PORTFOLIO OPERATIONS
    # ============================================
    
    def create_portfolio(self, name: str, description: str = "") -> Portfolio:
        """Create new portfolio"""
        db = self.get_session()
        try:
            portfolio = Portfolio(name=name, description=description)
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)  # Get the ID back
            return portfolio
        finally:
            db.close()
    
    def get_all_portfolios(self) -> List[Portfolio]:
        """Get all portfolios"""
        db = self.get_session()
        try:
            return db.query(Portfolio).all()
        finally:
            db.close()
    
    def get_portfolio(self, portfolio_id: int) -> Optional[Portfolio]:
        """Get portfolio by ID"""
        db = self.get_session()
        try:
            return db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        finally:
            db.close()
    
    def delete_portfolio(self, portfolio_id: int) -> bool:
        """Delete portfolio and all its stocks"""
        db = self.get_session()
        try:
            portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if portfolio:
                db.delete(portfolio)
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    # ============================================
    # STOCK OPERATIONS
    # ============================================
    
    def add_stock(
        self, 
        portfolio_id: int, 
        symbol: str, 
        shares: float, 
        purchase_price: float,
        purchase_date: datetime = None
    ) -> Optional[Stock]:
        """Add stock to portfolio"""
        db = self.get_session()
        try:
            stock = Stock(
                portfolio_id=portfolio_id,
                symbol=symbol.upper(),
                shares=shares,
                purchase_price=purchase_price,
                purchase_date=purchase_date or datetime.now()
            )
            db.add(stock)
            db.commit()
            db.refresh(stock)
            return stock
        finally:
            db.close()
    
    def get_portfolio_stocks(self, portfolio_id: int) -> List[Stock]:
        """Get all stocks in a portfolio"""
        db = self.get_session()
        try:
            return db.query(Stock).filter(Stock.portfolio_id == portfolio_id).all()
        finally:
            db.close()
    
    def delete_stock(self, stock_id: int) -> bool:
        """Remove stock from portfolio"""
        db = self.get_session()
        try:
            stock = db.query(Stock).filter(Stock.id == stock_id).first()
            if stock:
                db.delete(stock)
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    # ============================================
    # ANALYTICS
    # ============================================
    
    def save_price_snapshot(self, portfolio_id: int, total_value: float):
        """Save portfolio value for historical tracking"""
        db = self.get_session()
        try:
            snapshot = PriceHistory(
                portfolio_id=portfolio_id,
                total_value=total_value
            )
            db.add(snapshot)
            db.commit()
        finally:
            db.close()
    
    def get_price_history(self, portfolio_id: int) -> List[PriceHistory]:
        """Get historical portfolio values"""
        db = self.get_session()
        try:
            return db.query(PriceHistory)\
                .filter(PriceHistory.portfolio_id == portfolio_id)\
                .order_by(PriceHistory.recorded_date)\
                .all()
        finally:
            db.close()