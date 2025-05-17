# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code into the container
COPY . .

# Expose the port your app runs on (change if needed)
EXPOSE 5000

# Command to run your app (adjust for your entrypoint)
CMD ["python", "app.py"]