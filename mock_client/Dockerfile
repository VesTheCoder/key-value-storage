FROM python:3.11-slim

WORKDIR /app

# Install required packages
RUN pip install --no-cache-dir aiohttp

# Copy the client script
COPY ./client.py ./

# Run the client script
CMD ["python", "client.py"] 