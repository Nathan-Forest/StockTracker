# models/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from typing import List, Optional

# Base class for all models (like DbContext in C#)
Base = declarative_base()


class Portfolio(Base):
    """Portfolio model - like C# Portfolio class"""
    __tablename__ = 'portfolios'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_date = Column(DateTime, default=datetime.now)
    
    # Relationship: One portfolio has many stocks
    stocks = relationship('Stock', back_populates='portfolio', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, name='{self.name}')>"


class Stock(Base):
    """Stock holding model"""
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    shares = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
    purchase_date = Column(DateTime, default=datetime.now)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'))
    
    # Relationship: Each stock belongs to one portfolio
    portfolio = relationship('Portfolio', back_populates='stocks')
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost of this holding"""
        return self.shares * self.purchase_price
    
    def __repr__(self):
        return f"<Stock(symbol='{self.symbol}', shares={self.shares})>"


class PriceHistory(Base):
    """Track portfolio value over time"""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'))
    total_value = Column(Float, nullable=False)
    recorded_date = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<PriceHistory(portfolio_id={self.portfolio_id}, value=${self.total_value:.2f})>"


# Database setup
DATABASE_URL = 'sqlite:///stocktracker.db'
engine = create_engine(DATABASE_URL, echo=False)  # echo=True shows SQL queries

# Create session factory (like DbContext in C#)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Create all tables - like 'dotnet ef database update'"""
    Base.metadata.create_all(engine)
    print("✅ Database initialized!")


def get_db():
    """Get database session - like dependency injection in C#"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()