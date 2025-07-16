#!/bin/bash

set -e  # Exit on any error

echo "🚀 Starting Agri-Dashboard Setup on $(hostname)..."

# CONFIGURATION
APP_USER="namal"
APP_DIR="/home/$APP_USER/Namal_Agri_Dashboard"
APP_FILE="streamlit_app.py"
STREAMLIT_CMD=$(which streamlit)
SYSTEMD_SERVICE="/etc/systemd/system/streamlit-dashboard.service"

# 1. Install NGINX
echo "📦 Installing NGINX..."
sudo apt update && sudo apt install -y nginx

# 2. Configure NGINX reverse proxy
echo "🛠️ Configuring NGINX reverse proxy..."

sudo tee /etc/nginx/sites-available/agri_dashboard > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8501/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable site and reload NGINX
echo "🔗 Enabling NGINX site..."
sudo ln -sf /etc/nginx/sites-available/agri_dashboard /etc/nginx/sites-enabled/default

echo "🔁 Restarting NGINX..."
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# 3. Create systemd service for Streamlit
echo "⚙️ Setting up Streamlit as a systemd service..."

sudo tee $SYSTEMD_SERVICE > /dev/null <<EOF
[Unit]
Description=Streamlit Agri Dashboard
After=network.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=$STREAMLIT_CMD run $APP_FILE --server.port=8501 --server.headless=true
# ExecStart=/bin/bash -c "python3 mqtt_listner.py & exec $STREAMLIT_CMD run $APP_FILE --server.port=8501 --server.headless=true"
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable streamlit-dashboard.service
sudo systemctl start streamlit-dashboard.service

# 4. Open port 80 via UFW (if enabled)
if sudo ufw status | grep -q "Status: active"; then
    echo "🔓 Allowing HTTP traffic through UFW..."
    sudo ufw allow 80/tcp
else
    echo "⚠️ UFW not active — skipping firewall rule"
fi

echo "✅ Setup complete!"
echo "🌐 Access your dashboard at: http://$(hostname -I | awk '{print $1}')/"
