# stock_fetcher.py
import yfinance as yf

def get_stock_price(symbol):
    """
    Get current stock price for a given symbol
    
    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
    
    Returns:
        dict: Stock information
    """
    try:
        # Create ticker object
        stock = yf.Ticker(symbol)
        
        # Get current price
        info = stock.info
        
        # Extract relevant data
        return {
            'symbol': symbol,
            'name': info.get('longName', 'Unknown'),
            'current_price': info.get('currentPrice', 0),
            'previous_close': info.get('previousClose', 0),
            'change': info.get('currentPrice', 0) - info.get('previousClose', 0),
            'change_percent': ((info.get('currentPrice', 0) - info.get('previousClose', 0)) / info.get('previousClose', 1)) * 100
        }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def main():
    """Test the stock fetcher"""
    print("🐍 Stock Price Fetcher\n")
    
    # Test with a few popular stocks
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    
    for symbol in symbols:
        print(f"Fetching {symbol}...")
        stock_data = get_stock_price(symbol)
        
        if stock_data:
            print(f"  {stock_data['name']}")
            print(f"  Price: ${stock_data['current_price']:.2f}")
            print(f"  Change: ${stock_data['change']:.2f} ({stock_data['change_percent']:.2f}%)")
            print()
        else:
            print(f"  Failed to fetch {symbol}\n")


if __name__ == '__main__':
    main()