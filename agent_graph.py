# agent_graph.py
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from tools import get_price, buying_power_tool
import os
from dotenv import load_dotenv
import yfinance as yf

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the .env file
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OpenAI API key is missing in the .env file")

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    openai_api_key=openai_api_key
)

# Common stock tickers for validation
COMMON_TICKERS = {
    # Tech stocks
    'AAPL': 'Apple',
    'MSFT': 'Microsoft',
    'GOOGL': 'Google',
    'AMZN': 'Amazon',
    'META': 'Meta',
    'TSLA': 'Tesla',
    'NVDA': 'NVIDIA',
    'AMD': 'AMD',
    'INTC': 'Intel',
    'CRM': 'Salesforce',
    # Financial stocks
    'JPM': 'JPMorgan Chase',
    'BAC': 'Bank of America',
    'WFC': 'Wells Fargo',
    'GS': 'Goldman Sachs',
    'MS': 'Morgan Stanley',
    # Retail stocks
    'WMT': 'Walmart',
    'TGT': 'Target',
    'COST': 'Costco',
    'HD': 'Home Depot',
    'SBUX': 'Starbucks',
    'KO': 'Coca-Cola'
}

def extract_potential_ticker(text):
    """Extract potential stock ticker from text, handling various formats."""
    # First, look for tickers in the format "TICKER" or "$TICKER"
    patterns = [
        r'\b[A-Z]{1,5}\b',  # 1-5 capital letters
        r'\$[A-Z]{1,5}\b',  # Tickers with $ prefix
    ]
    
    # Convert common company names to tickers
    text_upper = text.upper()
    for ticker, company in COMMON_TICKERS.items():
        if company.upper() in text_upper:
            return ticker
    
    # Look for exact matches in common tickers first
    words = text_upper.split()
    for word in words:
        clean_word = word.strip('$')
        if clean_word in COMMON_TICKERS:
            return clean_word
    
    # Then try pattern matching
    for pattern in patterns:
        matches = re.findall(pattern, text_upper)
        if matches:
            # Filter out common English words and other noise
            for match in matches:
                clean_match = match.replace('$', '')
                # Skip if it's a common word that got caught
                if clean_match in ['A', 'I', 'ME', 'MY', 'AM', 'PM', 'THE', 'FOR', 'IN', 'IS', 'IT', 'BE', 'AS', 'AT', 'SO', 'WE', 'HE', 'BY', 'OR', 'ON', 'DO', 'IF', 'ME', 'UP', 'AN', 'GO', 'NO', 'US', 'OF']:
                    continue
                return clean_match
    return None

def is_valid_ticker(ticker):
    """Validate if a ticker is valid and has current market data."""
    if not ticker:
        return False
        
    # Check if it's in our common tickers list first
    if ticker in COMMON_TICKERS:
        return True
        
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return 'regularMarketPrice' in info and info['regularMarketPrice'] is not None
    except:
        return False

def agent_node(state):
    input_text = state["input"]
    chat_history = state.get("chat_history", [])
    
    # Extract potential ticker from input
    potential_ticker = extract_potential_ticker(input_text)
    
    # Look for context in chat history
    last_valid_ticker = None
    last_valid_amount = None
    
    # Scan recent history for context
    for msg in reversed(chat_history[:-1]):  # Exclude current message
        if msg["role"] == "user":
            hist_ticker = extract_potential_ticker(msg["content"])
            if hist_ticker and is_valid_ticker(hist_ticker):
                last_valid_ticker = hist_ticker
                # Look for amount in the same message
                amount_match = re.search(r'\$?(\d+(?:,\d+)*(?:\.\d+)?)', msg["content"])
                if amount_match:
                    last_valid_amount = float(amount_match.group(1).replace(',', ''))
                break
    
    # If no ticker in current input but we have context, use it
    if not potential_ticker and last_valid_ticker and any(word in input_text.lower() for word in ['it', 'this', 'that', 'stock', 'price', 'shares']):
        potential_ticker = last_valid_ticker
    
    # If no potential ticker found in a way that looks like a stock query
    if not potential_ticker and any(word in input_text.lower() for word in ['stock', 'price', 'ticker', 'share', 'market']):
        return {
            "output": """I noticed you're asking about stocks, but I couldn't identify a specific ticker symbol. 
            
Here are some examples of valid queries:
- Just type a ticker (e.g., 'AAPL' for Apple)
- Ask for a price (e.g., 'What's the price of MSFT?')
- Calculate shares (e.g., 'How many GOOGL shares can I buy with $10000?')

Common tickers:
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Google)
- AMZN (Amazon)
- META (Meta)
- TSLA (Tesla)"""
        }
    
    # If no stock-related terms found at all
    if not potential_ticker and not any(word in input_text.lower() for word in ['stock', 'price', 'ticker', 'share', 'market', 'buy', 'worth', 'cost', 'it', 'this', 'that']):
        return {
            "output": """I can help you with:
1. Getting stock prices (e.g., 'AAPL' or 'What's MSFT trading at?')
2. Calculating how many shares you can buy (e.g., 'How many GOOGL shares for $10000?')

Try typing a ticker symbol to get started!"""
        }
    
    # If we found a potential ticker, verify it
    if potential_ticker and not is_valid_ticker(potential_ticker):
        similar_tickers = [t for t in COMMON_TICKERS.keys() if any(c1 == c2 for c1, c2 in zip(t, potential_ticker))]
        suggestion = f"\n\nDid you mean one of these?\n" + "\n".join([f"- {t} ({COMMON_TICKERS[t]})" for t in similar_tickers]) if similar_tickers else ""
        
        return {"output": f"'{potential_ticker}' doesn't appear to be a valid stock ticker. Please check the symbol and try again.{suggestion}"}
    
    # Process the query
    try:
        # Check if the query is about buying power
        if any(word in input_text.lower() for word in ['buy', 'afford', 'purchase', 'get', 'shares']):
            # Extract amount from the query if present
            amount_match = re.search(r'\$?(\d+(?:,\d+)*(?:\.\d+)?)', input_text)
            amount = None
            if amount_match:
                amount = float(amount_match.group(1).replace(',', ''))
            elif last_valid_amount:  # Use amount from context if available
                amount = last_valid_amount
            
            if amount:
                result = buying_power_tool(f"{potential_ticker},{amount}")
            else:
                result = "Please specify a dollar amount to calculate how many shares you can buy. For example:\n'How many AAPL shares can I buy with $10000?'"
        else:
            # Default to getting the price
            result = get_price(potential_ticker)
            
        return {"output": result}
    except Exception as e:
        print(f"[LangGraph] Error: {e}")
        return {"output": "I encountered an error while processing your request. Please try again with a different query."}
