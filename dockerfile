# Use Ubuntu as the base image
FROM ubuntu:22.04

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99 

# Install dependencies, Chromium, and required libraries
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-tk \
    python3-dev \
    wget \
    curl \
    unzip \
    chromium-browser \
    xvfb \
    x11-utils \
    xauth \
    dbus-x11 \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    fonts-liberation \
    libgbm-dev \
    libu2f-udev \
    xdg-utils \
    gnupg \
    ca-certificates \
    tini

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose the port Flask runs on
EXPOSE 5000

# Use tini as the entrypoint to prevent process hanging
ENTRYPOINT ["/usr/bin/tini", "--"]

# Start the application using xvfb-run with proper arguments
CMD ["xvfb-run", "--server-args=-ac -noreset -screen 0 1920x1080x24", "python3", "main.py"]
