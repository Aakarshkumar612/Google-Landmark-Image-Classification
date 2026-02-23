# Use Python 3.11 for ML compatibility
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV/TensorFlow
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Run the backend
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
