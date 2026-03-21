# cli.py
from typing import Optional
from services.portfolio_service import PortfolioService
from data.db_manager import DatabaseManager
from datetime import datetime


class StockTrackerCLI:
    """Command-line interface for Stock Tracker"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.service = PortfolioService()
    
    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}")
    
    def print_portfolios(self):
        """Display all portfolios"""
        portfolios = self.db.get_all_portfolios()
        
        if not portfolios:
            print("\nNo portfolios found. Create one to get started!")
            return
        
        print(f"\n{'ID':<5} {'Name':<20} {'Description':<30} {'Created':<12}")
        print("-" * 70)
        
        for p in portfolios:
            created = p.created_date.strftime('%Y-%m-%d')
            desc = (p.description[:27] + '...') if len(p.description) > 30 else p.description
            print(f"{p.id:<5} {p.name:<20} {desc:<30} {created:<12}")
    
    def print_portfolio_summary(self, portfolio_id: int):
        """Display detailed portfolio summary"""
        summary = self.service.get_portfolio_summary(portfolio_id)
        
        if 'error' in summary:
            print(f"\n❌ {summary['error']}")
            return
        
        portfolio = summary['portfolio']
        
        self.print_header(f"Portfolio: {portfolio.name}")
        
        if portfolio.description:
            print(f"Description: {portfolio.description}")
        
        if not summary['stocks']:
            print("\n📭 No stocks in this portfolio yet.")
            return
        
        # Print stocks
        print(f"\n{'Symbol':<8} {'Name':<25} {'Shares':<10} {'Buy $':<12} {'Now $':<12} {'Value $':<12} {'Gain/Loss':<15}")
        print("-" * 110)
        
        for stock in summary['stocks']:
            if 'error' in stock:
                print(f"{stock['symbol']:<8} {'Error fetching price':<25}")
                continue
            
            gain_loss_color = '🟢' if stock['gain_loss'] >= 0 else '🔴'
            gain_loss_str = f"{gain_loss_color} ${stock['gain_loss']:,.2f} ({stock['gain_loss_percent']:+.2f}%)"
            
            print(f"{stock['symbol']:<8} "
                  f"{stock['name'][:24]:<25} "
                  f"{stock['shares']:<10.2f} "
                  f"${stock['purchase_price']:<11,.2f} "
                  f"${stock['current_price']:<11,.2f} "
                  f"${stock['current_value']:<11,.2f} "
                  f"{gain_loss_str:<15}")
        
        # Print totals
        print("-" * 110)
        total_color = '🟢' if summary['total_gain_loss'] >= 0 else '🔴'
        print(f"\n{'TOTAL':<61} "
              f"${summary['total_cost']:,.2f} → ${summary['total_value']:,.2f}")
        print(f"{'Gain/Loss:':<61} "
              f"{total_color} ${summary['total_gain_loss']:,.2f} ({summary['total_gain_loss_percent']:+.2f}%)")
    
    def create_portfolio_interactive(self):
        """Interactive portfolio creation"""
        self.print_header("Create New Portfolio")
        
        name = input("\nPortfolio name: ").strip()
        if not name:
            print("❌ Name cannot be empty!")
            return
        
        description = input("Description (optional): ").strip()
        
        portfolio = self.db.create_portfolio(name, description)
        print(f"\n✅ Created portfolio: {portfolio.name} (ID: {portfolio.id})")
    
    def add_stock_interactive(self):
        """Interactive stock addition"""
        self.print_header("Add Stock to Portfolio")
        
        # Show portfolios
        self.print_portfolios()
        
        try:
            portfolio_id = int(input("\nEnter portfolio ID: "))
            
            # Verify portfolio exists
            portfolio = self.db.get_portfolio(portfolio_id)
            if not portfolio:
                print(f"❌ Portfolio {portfolio_id} not found!")
                return
            
            symbol = input("Stock symbol (e.g., AAPL): ").strip().upper()
            shares = float(input("Number of shares: "))
            purchase_price = float(input("Purchase price per share: $"))
            
            # Optional: purchase date
            use_custom_date = input("Use custom purchase date? (y/n): ").lower() == 'y'
            purchase_date = None
            
            if use_custom_date:
                date_str = input("Purchase date (YYYY-MM-DD): ")
                try:
                    purchase_date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    print("⚠️ Invalid date format, using today's date")
            
            stock = self.db.add_stock(portfolio_id, symbol, shares, purchase_price, purchase_date)
            print(f"\n✅ Added {shares} shares of {symbol} to {portfolio.name}")
            
        except ValueError:
            print("❌ Invalid input! Please enter numbers correctly.")
    
    def main_menu(self):
        """Main menu loop"""
        while True:
            self.print_header("📊 Stock Portfolio Tracker")
            print("\n1. View all portfolios")
            print("2. View portfolio details")
            print("3. Create new portfolio")
            print("4. Add stock to portfolio")
            print("5. Delete portfolio")
            print("6. Exit")
            
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == '1':
                self.print_portfolios()
            
            elif choice == '2':
                try:
                    portfolio_id = int(input("\nEnter portfolio ID: "))
                    self.print_portfolio_summary(portfolio_id)
                except ValueError:
                    print("❌ Invalid ID!")
            
            elif choice == '3':
                self.create_portfolio_interactive()
            
            elif choice == '4':
                self.add_stock_interactive()
            
            elif choice == '5':
                try:
                    portfolio_id = int(input("\nEnter portfolio ID to delete: "))
                    confirm = input(f"⚠️ Delete portfolio {portfolio_id}? This cannot be undone! (yes/no): ")
                    if confirm.lower() == 'yes':
                        if self.db.delete_portfolio(portfolio_id):
                            print(f"✅ Portfolio {portfolio_id} deleted!")
                        else:
                            print(f"❌ Portfolio {portfolio_id} not found!")
                except ValueError:
                    print("❌ Invalid ID!")
            
            elif choice == '6':
                print("\n👋 Thanks for using Stock Tracker!")
                break
            
            else:
                print("❌ Invalid choice! Please enter 1-6.")
            
            input("\nPress Enter to continue...")


if __name__ == '__main__':
    cli = StockTrackerCLI()
    cli.main_menu()