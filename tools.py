# tools.py

import yfinance as yf

def get_price(ticker):
    """Get the current price of a stock by its ticker symbol."""
    try:
        # Clean the ticker symbol
        ticker = ticker.strip().upper()
        stock = yf.Ticker(ticker)
        
        # Get the stock info
        info = stock.info
        if 'regularMarketPrice' not in info or info['regularMarketPrice'] is None:
            return f"Could not get the current price for {ticker}. Please verify the ticker symbol."
            
        price = info['regularMarketPrice']
        company_name = info.get('longName', ticker)
        
        return f"The current price of {company_name} ({ticker}) is ${price:.2f}"
    except Exception as e:
        return f"Error getting price for {ticker}: {str(e)}"

def buying_power_tool(query):
    """Calculate how many shares you can buy with a specified dollar amount."""
    try:
        # Parse input
        if ',' not in query:
            return "Please provide input in the format: TICKER,AMOUNT (e.g., 'AAPL,20000')"
            
        ticker, amount = query.split(',', 1)
        ticker = ticker.strip().upper()
        
        try:
            amount = float(amount.strip())
        except ValueError:
            return f"Invalid amount provided: {amount}. Please provide a valid number."
            
        if amount <= 0:
            return "Please provide a positive dollar amount."
            
        # Get stock price
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if 'regularMarketPrice' not in info or info['regularMarketPrice'] is None:
            return f"Could not get the current price for {ticker}. Please verify the ticker symbol."
            
        price = info['regularMarketPrice']
        company_name = info.get('longName', ticker)
        shares = int(amount // price)
        
        return f"With ${amount:,.2f}, you can buy {shares:,} shares of {company_name} ({ticker}) at ${price:.2f} per share."
    except Exception as e:
        return f"Error calculating buying power: {str(e)}"
