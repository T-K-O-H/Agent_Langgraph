import os
import chainlit as cl
from agent_graph import agent_node
from dotenv import load_dotenv  # Import dotenv
from typing import List, Dict

# Load environment variables from .env file
load_dotenv()

# Ensure your OpenAI API key is set up in environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OpenAI API key is missing in the .env file")

# Store chat history
chat_histories: Dict[str, List[Dict[str, str]]] = {}

@cl.on_chat_start
async def start_chat():
    # Initialize empty chat history for this session
    chat_histories[cl.user_session.get("id")] = []
    
    welcome_message = """👋 Welcome to the Stock Price Calculator!

I can help you with:
• Getting real-time stock prices
• Calculating how many shares you can buy

Try these examples:
• Type 'AAPL' to get Apple's stock price
• Ask 'How many MSFT shares can I buy with $10000?'

What would you like to know?"""
    
    await cl.Message(content=welcome_message).send()

@cl.on_message
async def handle_message(message: cl.Message):
    try:
        # Get chat history for this session
        session_id = cl.user_session.get("id")
        history = chat_histories.get(session_id, [])
        
        # Add current message to history
        history.append({"role": "user", "content": message.content})
        
        # Create state dictionary with history
        state = {
            "input": message.content,
            "chat_history": history
        }
        
        # Process the message with agent_node
        response = agent_node(state)
        
        # Send the response back to the user
        if isinstance(response, dict) and "output" in response:
            # Add response to history
            history.append({"role": "assistant", "content": response["output"]})
            await cl.Message(content=response["output"]).send()
        else:
            await cl.Message(content="Received an invalid response format from the agent.").send()
            
        # Update history in storage
        chat_histories[session_id] = history
            
    except Exception as e:
        print(f"Error occurred: {e}")
        await cl.Message(content="Sorry, something went wrong while processing your request.").send()

@cl.on_chat_end
async def end_chat():
    # Clean up chat history when session ends
    session_id = cl.user_session.get("id")
    if session_id in chat_histories:
        del chat_histories[session_id]
