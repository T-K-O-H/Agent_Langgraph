---
title: AI Stock Price Assistant
emoji: 📈
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# AI Stock Price Assistant 📈

A real-time stock price and share calculator powered by ChatGPT and Yahoo Finance.

## Features

- 🔍 Get real-time stock prices for any ticker
- 💰 Calculate how many shares you can buy with a specific amount
- 💬 Natural language understanding (e.g., "What's Apple's stock price?")
- 🧠 Context-aware conversations (remembers previous stocks discussed)
- 📊 Support for all major stock exchanges

## Examples

1. Check stock prices:
   ```
   AAPL
   What's the price of Microsoft?
   Show me GOOGL
   ```

2. Calculate shares:
   ```
   How many AAPL shares can I buy with $10000?
   What can I get of Tesla for $5000?
   ```

3. Context-aware queries:
   ```
   MSFT
   How many shares for $20000?
   What about $30000?
   ```

## Technical Details

- Built with Chainlit for the chat interface
- Uses LangChain for natural language processing
- Real-time data from Yahoo Finance
- OpenAI GPT-4 for natural language understanding

## Environment Variables

You need to set up the following environment variables:
```
OPENAI_API_KEY=your-api-key-here
```

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your .env file with your OpenAI API key
4. Run the app:
   ```bash
   chainlit run app.py
   ```

## Deployment

This app is deployed on Hugging Face Spaces. You can find it at:
https://huggingface.co/spaces/Shipmaster1/AI_Stock_Agent

## License

MIT License - feel free to use and modify! 