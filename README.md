# Namal Agri Dashboard

This project provides a comprehensive solution for collecting, storing, and visualizing agricultural sensor data in real-time. It consists of an MQTT listener to capture sensor data, a Streamlit web application for data visualization, and setup scripts for easy deployment.

## Features

-   **Real-time Data Ingestion**: An MQTT listener subscribes to a topic to receive sensor data from IoT devices.
-   **Robust Data Parsing**: The listener can handle various JSON formats, including double-encoded and unescaped strings.
-   **Data Storage**: Sensor data is stored in both CSV (`sensor_data.csv`) and JSON (`sensor_data.json`) formats.
-   **Interactive Dashboard**: A multi-page Streamlit application visualizes the data with interactive charts, gauges, and metrics.
-   **Automated Setup**: Shell scripts are provided to automate the setup of the MQTT listener and Streamlit dashboard as systemd services.

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

-   `mqtt_listener.py`: The Python script that listens for MQTT messages and saves them.
-   `streamlit_app.py`: The main application file for the Streamlit dashboard.
-   `requirements.txt`: A list of Python dependencies for the project.
-   `sensor_data.csv`: CSV file for storing sensor data.
-   `sensor_data.json`: JSON file for storing sensor data.
-   `setup_agri_dashboard.sh`: A shell script to automate the deployment of the Streamlit dashboard.
-   `setup_mqtt_listener.sh`: A shell script to set up the MQTT listener as a `systemd` service.
-   `mqtt-listener.service`: A `systemd` service file for the MQTT listener.
-   `.gitignore`: Specifies files and directories to be ignored by Git.

## Troubleshooting

-   **`streamlit run` command not found**: Ensure you have installed the dependencies from `requirements.txt` and that the `streamlit` executable is in your system's `PATH`.
-   **MQTT connection errors**: Check that your MQTT broker is running and that the `broker_address` and `port` in `mqtt_listener.py` are correct.
-   **Dashboard not updating**: Verify that the `mqtt_listener.py` script is running and that new data is being written to `sensor_data.json`.
