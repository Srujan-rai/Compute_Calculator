# Base image with Python
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    xvfb \
    xauth \
    libxrender1 \
    libxext6 \
    libxi6 \
    python3-tk \
    chromium \
    chromium-driver \
    && apt-get clean

# Set environment variables for X11
ENV DISPLAY=:99
ENV XAUTHORITY=/root/.Xauthority
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app

# Expose Flask's default port
EXPOSE 5000

# Start Xvfb and the Flask app
CMD ["sh", "-c", "Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp & python app.py"]
 