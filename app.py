# app.py
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from services.portfolio_service import PortfolioService
from data.db_manager import DatabaseManager
from datetime import datetime
from typing import Dict, List
import os

# Configuration for different environments
PORT = int(os.environ.get('PORT', 5000))
HOST = os.environ.get('HOST', '0.0.0.0')
DEBUG = os.environ.get('FLASK_ENV', 'development') != 'production'

# Initialize Flask app (like Program.cs in C#)
app = Flask(__name__)
CORS(app)  # Enable CORS (like C# CORS policy)

# Initialize services (like dependency injection in C#)
db = DatabaseManager()
portfolio_service = PortfolioService()


# ============================================
# HTML ROUTES (Pages)
# ============================================

@app.route('/')
def index():
    """Home page - list all portfolios"""
    return render_template('index.html')


@app.route('/portfolio/<int:portfolio_id>')
def portfolio_detail(portfolio_id: int):
    """Portfolio detail page"""
    return render_template('portfolio.html', portfolio_id=portfolio_id)


# ============================================
# API ROUTES (Like C# Controllers!)
# ============================================

@app.route('/api/portfolios', methods=['GET'])
def get_portfolios():
    """GET all portfolios - like C# [HttpGet]"""
    portfolios = db.get_all_portfolios()
    
    return jsonify([
        {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'created_date': p.created_date.isoformat()
        }
        for p in portfolios
    ])


@app.route('/api/portfolios', methods=['POST'])
def create_portfolio():
    """POST create portfolio - like C# [HttpPost]"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    portfolio = db.create_portfolio(
        name=data['name'],
        description=data.get('description', '')
    )
    
    return jsonify({
        'id': portfolio.id,
        'name': portfolio.name,
        'description': portfolio.description,
        'created_date': portfolio.created_date.isoformat()
    }), 201


@app.route('/api/portfolios/<int:portfolio_id>', methods=['DELETE'])
def delete_portfolio(portfolio_id: int):
    """DELETE portfolio - like C# [HttpDelete]"""
    if db.delete_portfolio(portfolio_id):
        return jsonify({'message': 'Portfolio deleted successfully'})
    return jsonify({'error': 'Portfolio not found'}), 404


@app.route('/api/portfolios/<int:portfolio_id>/summary', methods=['GET'])
def get_portfolio_summary(portfolio_id: int):
    """GET portfolio summary with calculations"""
    summary = portfolio_service.get_portfolio_summary(portfolio_id)
    
    if 'error' in summary:
        return jsonify(summary), 404
    
    # Convert objects to JSON-serializable dicts
    return jsonify({
        'portfolio': {
            'id': summary['portfolio'].id,
            'name': summary['portfolio'].name,
            'description': summary['portfolio'].description
        },
        'stocks': summary['stocks'],
        'total_cost': summary['total_cost'],
        'total_value': summary['total_value'],
        'total_gain_loss': summary['total_gain_loss'],
        'total_gain_loss_percent': summary['total_gain_loss_percent']
    })


@app.route('/api/portfolios/<int:portfolio_id>/stocks', methods=['POST'])
def add_stock(portfolio_id: int):
    """POST add stock to portfolio"""
    data = request.get_json()
    
    required_fields = ['symbol', 'shares', 'purchase_price']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Parse optional purchase date
        purchase_date = None
        if 'purchase_date' in data:
            purchase_date = datetime.fromisoformat(data['purchase_date'])
        
        stock = db.add_stock(
            portfolio_id=portfolio_id,
            symbol=data['symbol'].upper(),
            shares=float(data['shares']),
            purchase_price=float(data['purchase_price']),
            purchase_date=purchase_date
        )
        
        return jsonify({
            'id': stock.id,
            'symbol': stock.symbol,
            'shares': stock.shares,
            'purchase_price': stock.purchase_price,
            'purchase_date': stock.purchase_date.isoformat()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/portfolios/<int:portfolio_id>/stocks/<int:stock_id>', methods=['DELETE'])
def delete_stock(portfolio_id: int, stock_id: int):
    """DELETE stock from portfolio"""
    if db.delete_stock(stock_id):
        return jsonify({'message': 'Stock deleted successfully'})
    return jsonify({'error': 'Stock not found'}), 404


@app.route('/api/portfolios/<int:portfolio_id>/history', methods=['GET'])
def get_price_history(portfolio_id: int):
    """GET historical portfolio values"""
    history = db.get_price_history(portfolio_id)
    
    return jsonify([
        {
            'date': h.recorded_date.isoformat(),
            'value': h.total_value
        }
        for h in history
    ])


# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    print("🚀 Starting Stock Tracker Web Server...")
    print(f"📊 Open http://localhost:{PORT} in your browser")
    print(f"🔧 Environment: {'Production' if not DEBUG else 'Development'}")
    app.run(debug=DEBUG, host=HOST, port=PORT)