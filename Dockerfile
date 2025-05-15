FROM python:3.11-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy source code
COPY ./source ./source
COPY ./test.db ./

# Expose port
EXPOSE 6969

# Set environment variables
ENV APP_HOST=0.0.0.0
ENV APP_PORT=6969
ENV DEBUG=True
ENV DB_URL=sqlite+aiosqlite:///test.db

# Run the server
CMD ["python", "-m", "source.main"]
