FROM python:3.10-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /code/

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=7860
ENV PYTHONPATH=/code

# Command to run the application
CMD chainlit run app.py --host $HOST --port $PORT 