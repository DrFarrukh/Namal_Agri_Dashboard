# Namal Agri Dashboard

This project provides a comprehensive solution for collecting, storing, and visualizing agricultural sensor data in real-time. It consists of an MQTT listener to capture sensor data, a Streamlit web application for data visualization, and setup scripts for easy deployment.

**Developed by**: Electrical Engineering Department, Namal University, Mianwali, Pakistan

## Features

-   **Real-time Data Ingestion**: An MQTT listener subscribes to a topic to receive sensor data from IoT devices.
-   **Robust Data Parsing**: The listener can handle various JSON formats, including double-encoded and unescaped strings.
-   **Data Validation**: Real-time validation of sensor readings against scientific ranges - invalid data is rejected before storage.
-   **Data Quality Assurance**: Built-in validation ensures all stored data is within acceptable physical/scientific ranges.
-   **Dual Data Storage**: Sensor data is stored in both CSV (`sensor_data.csv`) and JSON (`sensor_data.json`) formats for flexibility.
-   **Interactive Dashboard**: A multi-page Streamlit application visualizes the data with interactive charts, gauges, and metrics.
-   **Multi-Page Interface**: Dashboard, Detailed Analysis, Historical Data, and About pages.
-   **Pakistan Time Support**: All timestamps displayed in Pakistan Standard Time (PKT).
-   **Data Export**: Export filtered data to CSV or JSON formats.
-   **Automated Insights**: AI-powered recommendations based on sensor readings and optimal ranges.
-   **Data Cleaning Tools**: Utility script to clean existing data by removing duplicates and invalid values.
-   **Automated Setup**: Shell scripts are provided to automate the setup of the MQTT listener and Streamlit dashboard as systemd services.

## Monitored Parameters

### Soil Parameters
-   **Soil Moisture**: Water content percentage (Validated: 0-100%)
-   **Soil Nitrogen**: Nitrogen content (Validated: 0-200 mg/kg)
-   **Soil Phosphorus**: Phosphorus content (Validated: 0-150 mg/kg)
-   **Soil Potassium**: Potassium content (Validated: 0-500 mg/kg)
-   **Soil Temperature**: Temperature in Celsius (Validated: -10 to 60°C)
-   **Soil Conductivity**: Electrical conductivity (Validated: 0-200 mS/cm)
-   **Soil pH**: Acidity/alkalinity level (Validated: 3.0-10.0 pH)

### Air Parameters
-   **Air Temperature**: Ambient temperature (Validated: -40 to 60°C)
-   **Air Humidity**: Relative humidity percentage (Validated: 0-100%)

### Data Validation
All sensor readings are validated in real-time before storage. Values outside the specified ranges are **rejected and logged** to maintain data integrity for accurate analysis and machine learning applications.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

-   Python 3.8 or higher
-   `pip` (Python package installer)
-   `git` (for cloning the repository)
-   An MQTT broker (e.g., Mosquitto). You can install it on Debian/Ubuntu with:
    ```bash
    sudo apt update
    sudo apt install -y mosquitto mosquitto-clients
    ```

## Setup and Installation

Follow these steps to set up and run the project:

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/DrFarrukh/Namal_Agri_Dashboard.git
cd Namal_Agri_Dashboard
```

### 2. Install Python Dependencies

Install the required Python libraries using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 3. Set Up the MQTT Listener

The MQTT listener is responsible for capturing and storing the sensor data. You can run it as a background service or in a `screen` session.

#### Option A: Run as a `systemd` Service (Recommended for Production)

If you have `sudo` privileges, you can set up the MQTT listener as a `systemd` service that will run automatically in the background.

1.  **Run the setup script**:

    ```bash
    sudo ./setup_mqtt_listener.sh
    ```

2.  **Verify the service is running**:

    ```bash
    systemctl status mqtt-listener.service
    ```

3.  **View logs**:

    Logs are stored in `mqtt.log` and `mqtt_error.log` in the project directory.

#### Option B: Run in a `screen` Session (for Development)

If you don't have `sudo` privileges or prefer to run the listener manually, you can use `screen`.

1.  **Start a new `screen` session**:

    ```bash
    screen -S mqtt_listener
    ```

2.  **Run the listener script**:

    ```bash
    python3 mqtt_listener.py
    ```

3.  **Detach from the session**: Press `Ctrl+A` then `D` to leave the script running in the background.

4.  **Re-attach to the session**:

    ```bash
    screen -r mqtt_listener
    ```

### 4. Set Up the Streamlit Dashboard

The Streamlit dashboard provides a web interface to visualize the sensor data. You can deploy it as a service with NGINX or run it locally for development.

#### Option A: Deploy with NGINX and `systemd` (Recommended for Production)

This method sets up the Streamlit app as a `systemd` service and uses NGINX as a reverse proxy, making the dashboard accessible on port 80.

1.  **Run the setup script**:

    ```bash
    sudo ./setup_agri_dashboard.sh
    ```

2.  **Access the dashboard**: Open your web browser and navigate to your server's IP address (e.g., `http://<your_server_ip>`).

#### Option B: Run Locally (for Development)

To run the Streamlit app locally for development or testing:

1.  **Run the Streamlit command**:

    ```bash
    streamlit run streamlit_app.py
    ```

2.  **Access the dashboard**: Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

## File Descriptions

### Core Application Files
-   `mqtt_listener.py`: MQTT listener with real-time data validation - rejects invalid sensor readings.
-   `streamlit_app.py`: Multi-page Streamlit dashboard with interactive visualizations and AI insights.
-   `clean_sensor_data.py`: Utility script to clean existing data files (remove duplicates, invalid values, outliers).
-   `requirements.txt`: Python dependencies (paho-mqtt, streamlit, pandas, plotly, numpy, pytz).

### Data Files
-   `sensor_data.csv`: Validated sensor data in CSV format (18,839 clean records).
-   `sensor_data.json`: Validated sensor data in JSON format (18,839 clean records).
-   `sensor_data_backup.csv`: Backup of original data before cleaning.
-   `sensor_data_backup.json`: Backup of original data before cleaning.

### Deployment Scripts
-   `setup_agri_dashboard.sh`: Automates Streamlit dashboard deployment with NGINX.
-   `setup_mqtt_listener.sh`: Sets up MQTT listener as a systemd service.
-   `mqtt-listener.service`: Systemd service configuration for MQTT listener.

### Assets
-   `agri_img.jpg`: Dashboard image asset.
-   `.gitignore`: Git ignore rules.

## Dashboard Pages

The Streamlit application includes four main pages:

1. **Dashboard**: Real-time sensor readings with gauge visualizations, time-series charts, and AI-powered insights.
2. **Detailed Analysis**: Statistical summaries, correlation heatmaps, moving averages, and distribution analysis.
3. **Historical Data**: Date range filtering, data aggregation (hourly/daily/weekly), and data export functionality.
4. **About**: Project information, monitored parameters, and technology stack details.

## Service Management

### Check Service Status
```bash
# Check MQTT listener status
systemctl status mqtt-listener.service

# Check Streamlit dashboard status
systemctl status streamlit-dashboard.service

# Check NGINX status
systemctl status nginx
```

### View Logs
```bash
# MQTT listener logs
tail -f /home/namal/Namal_Agri_Dashboard/mqtt_error.log

# Streamlit logs
journalctl -u streamlit-dashboard.service -f

# NGINX logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
# Restart MQTT listener
sudo systemctl restart mqtt-listener.service

# Restart Streamlit dashboard
sudo systemctl restart streamlit-dashboard.service

# Restart NGINX
sudo systemctl restart nginx
```

## Troubleshooting

### Common Issues and Solutions

-   **`streamlit run` command not found**: 
    - Ensure you have installed the dependencies from `requirements.txt`
    - Check that the `streamlit` executable is in your system's `PATH`
    - Try: `pip install --user streamlit` or `pip3 install streamlit`

-   **MQTT connection errors**: 
    - Check that your MQTT broker is running: `systemctl status mosquitto`
    - Verify the `broker_address` and `port` in `mqtt_listener.py` are correct
    - Test MQTT broker: `mosquitto_sub -h localhost -t agri_sensor/data -v`

-   **Dashboard not updating**: 
    - Verify that the `mqtt_listener.py` script is running: `systemctl status mqtt-listener.service`
    - Check that new data is being written to `sensor_data.json`: `tail -f sensor_data.json`
    - Review MQTT logs: `tail -f mqtt_error.log`

-   **Port 80 access denied**:
    - Ensure NGINX is running: `systemctl status nginx`
    - Check firewall settings: `sudo ufw status`
    - Verify NGINX configuration: `sudo nginx -t`

-   **Data file too large / Performance issues**:
    - Consider implementing data retention policy (archive old data)
    - Use database backend (PostgreSQL/InfluxDB) for better performance
    - Optimize by filtering data in dashboard queries

## Data Quality & Validation

### Real-time Validation
The MQTT listener validates all incoming sensor data against scientific ranges:
- Values outside acceptable ranges are **rejected and not stored**
- Validation errors are logged for debugging
- MAC addresses must follow standard format (XX:XX:XX:XX:XX:XX)

### Data Cleaning
Run the cleaning script on existing data:
```bash
python3 clean_sensor_data.py
```
This script:
- Removes duplicate records
- Filters out invalid/out-of-range values
- Creates backups before cleaning
- Provides detailed cleaning statistics

**Current Dataset**: 18,839 validated records from 3 sensor nodes

## Configuration

### MQTT Broker Settings
Edit `mqtt_listener.py` to configure:
```python
broker_address = "localhost"  # Change to your MQTT broker IP
port = 1883                    # Default MQTT port
topic = "agri_sensor/data"    # MQTT topic to subscribe
```

### Validation Ranges
Modify `VALIDATION_RANGES` in `mqtt_listener.py` to adjust acceptable sensor value ranges.

### Dashboard Settings
The dashboard auto-refreshes by default. You can configure:
- Refresh interval (5-60 seconds)
- Time frame filters (hour, day, week, month, quarter, 6 months, year)
- Data aggregation level (hourly, daily, weekly)

## Technology Stack

-   **Backend**: Python 3.8+
-   **MQTT Client**: paho-mqtt
-   **Web Framework**: Streamlit
-   **Data Visualization**: Plotly
-   **Data Processing**: Pandas, NumPy
-   **Timezone Handling**: pytz (Pakistan Standard Time)
-   **Web Server**: NGINX (reverse proxy)
-   **Service Management**: systemd
-   **Storage**: CSV + JSON files

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is developed by the Electrical Engineering Department at Namal University, Mianwali, Pakistan.

## Contact

For questions or support, please contact the Electrical Engineering Department at Namal University.

---

**Copyright © 2025 Farrukh Qureshi. All Rights Reserved.**
