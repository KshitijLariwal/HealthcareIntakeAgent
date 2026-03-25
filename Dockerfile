# Use the official, lightweight Python 3.12 image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /workspace

# Copy your requirements first to leverage Docker layer caching
COPY app/requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Change to the app directory so Uvicorn finds main.py
WORKDIR /workspace/app

# Expose the port the API will run on
EXPOSE 8000

# Command to run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]