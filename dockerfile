# Use Ubuntu as the base image
FROM ubuntu:20.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    xvfb \
    xauth \
    libxrender1 \
    libxext6 \
    libxi6 \
    python3 \
    python3-pip \
    python3-tk \
    chromium-browser \
    x11vnc \
    && apt-get clean

# Install ChromeDriver for Selenium
RUN wget -q https://chromedriver.storage.googleapis.com/113.0.5672.63/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

# Set up the display environment
ENV DISPLAY=:99

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app

# Expose Flask API and VNC server ports
EXPOSE 5000 5900

# Start Xvfb, VNC server, and the Flask app
CMD ["sh", "-c", "Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp -ac & x11vnc -display :99 -N -forever -rfbport 5900 & python3 app.py"]
