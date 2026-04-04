FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port and define volume
EXPOSE 8000
VOLUME ["/app/data"]

# Run application
CMD ["sh", "-c","uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT"]
