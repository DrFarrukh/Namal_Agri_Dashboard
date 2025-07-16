#!/bin/bash

set -e  # Exit on any error

echo "🚀 Starting MQTT Listener Service Setup on $(hostname)..."

# CONFIGURATION
APP_USER="namal"
APP_DIR="/home/$APP_USER/Namal_Agri_Dashboard"
SERVICE_FILE="$APP_DIR/mqtt-listener.service"
SERVICE_NAME="mqtt-listener.service"
PYTHON_EXEC="/usr/bin/python3"
SCRIPT_NAME="mqtt_listener.py"

# 1. Create systemd service file in local directory
echo "📄 Creating service file at $SERVICE_FILE..."

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=MQTT Listener for Agri Dashboard
After=network.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
ExecStart=$PYTHON_EXEC $APP_DIR/$SCRIPT_NAME
Restart=always
RestartSec=5
Environment="PYTHONUNBUFFERED=1"
StandardOutput=append:$APP_DIR/mqtt.log
StandardError=append:$APP_DIR/mqtt_error.log

[Install]
WantedBy=multi-user.target
EOF

# 2. Link the service to systemd
echo "🔗 Linking $SERVICE_NAME to /etc/systemd/system/..."
sudo ln -sf $SERVICE_FILE /etc/systemd/system/$SERVICE_NAME

# 3. Reload systemd, enable and start the service
echo "🔄 Reloading systemd and starting MQTT Listener service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo "✅ MQTT Listener Service is now active."
