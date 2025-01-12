FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy only requirements to leverage Docker's caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port the server will run on (default FastAPI port is 8000)
EXPOSE 8000

# Command to run FastAPI server
CMD ["uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"]