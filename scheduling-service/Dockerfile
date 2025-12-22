# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements file first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Expose port 8003 for the scheduling service
EXPOSE 8003

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]