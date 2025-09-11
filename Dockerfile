# Smart Agriculture Sensor Dashboard
# Multi-service application for monitoring crop sensor data via MQTT
# Includes Streamlit dashboard, MQTT listener, and Mosquitto broker
# 
# Copyright (c) 2025 Qureshi. All rights reserved.
# 
# This software is proprietary and confidential. Unauthorized copying of this file,
# via any medium is strictly prohibited. This software is provided "as is" without
# warranty of any kind, express or implied, including but not limited to the
# warranties of merchantability, fitness for a particular purpose and noninfringement.
# 
# For licensing information, please contact: [contact information]
# Version: 1.0.0
# Build Date: 2025
# 
# Dependencies:
# - Python 3.11+
# - Streamlit for web dashboard
# - MQTT client for sensor data communication
# - Docker and Docker Compose for containerization

# Use lightweight Python base image for better performance and smaller size
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for Python packages compilation
# Clean up package cache to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker layer caching
# This allows dependency installation to be cached if requirements.txt hasn't changed
COPY requirements.txt .

# Install Python packages without cache to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
# This is done after dependency installation to optimize build caching
COPY . .

# Expose the port that Streamlit will run on
EXPOSE 8501

# Set default command to run Streamlit application
# This can be overridden by docker-compose service configuration
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
