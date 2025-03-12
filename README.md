# Project Description

This project comprises three main components working together to collect, store, and visualize agricultural sensor data. It uses MQTT for real-time data ingestion, CSV for data storage, and Streamlit for creating an interactive dashboard.

-   **`mqtt_listener.py`**: A Python script that acts as an MQTT client, subscribing to a specified topic (`agri_sensor/data`) on an MQTT broker (default: `localhost`). It receives sensor data in JSON format over MQTT and saves it to a CSV file (`sensor_data.csv`). This script is designed to handle potential invalid JSON formats by attempting to fix them before parsing. It also includes logging for debugging and monitoring.

-   **`sensor_data.csv`**: This CSV (Comma Separated Values) file serves as the data storage for the sensor readings. Each row in the CSV represents a sensor data point, with columns for timestamp and various sensor parameters such as soil moisture, temperature, humidity, pH, and nutrient levels (nitrogen, phosphorus, potassium), as well as air temperature and humidity. The CSV file is initialized with a header row containing these field names.

-   **`streamlit_app.py`**: A Python script that builds an interactive web dashboard using the Streamlit framework. This application reads the `sensor_data.csv` file and provides real-time visualization and analysis of the sensor data. The dashboard is designed with multiple pages for different levels of data exploration:
    -   **Dashboard**: Provides a high-level overview with key metrics displayed as gauges and metric cards, along with interactive time series charts for trend analysis and insightful summaries.
    -   **Detailed Analysis**: Allows users to delve deeper into specific sensor parameters, offering statistical summaries, time series analysis with moving averages, correlation heatmaps, distribution histograms, and scatter plot matrices.
    -   **Historical Data**: Enables users to explore historical data within specific date ranges, compare parameters over time, aggregate data by different time intervals (hour, day, week), and export filtered data to CSV or JSON formats.
    -   **About**: Provides a description of the dashboard, the parameters monitored, the data collection process, and the technologies used in the project.

## Usage

1.  **Start the MQTT Broker**: Ensure an MQTT broker (like Mosquitto) is running, especially if modifying `broker_address` in `mqtt_listener.py`. If using the default `localhost`, Mosquitto should be running locally.

2.  **Run `mqtt_listener.py`**: Execute this script to begin listening for MQTT messages.
    ```bash
    python mqtt_listener.py
    ```
    This script will continuously run and append new sensor data to `sensor_data.csv` as it arrives via MQTT.

3.  **Run `streamlit_app.py`**: Execute this script to launch the Streamlit dashboard.
    ```bash
    streamlit run streamlit_app.py
    ```
    This command will open the dashboard in your web browser (usually at `http://localhost:8501`).

4.  **Access the Dashboard**: Open your web browser and go to the address provided by Streamlit in the terminal (usually `http://localhost:8501`). You can then navigate through the different pages of the dashboard to view real-time sensor data, perform detailed analysis, and explore historical trends.

## Files Description

-   **`mqtt_listener.py`**:
    -   Subscribes to the `agri_sensor/data` MQTT topic.
    -   Connects to the MQTT broker at `localhost:1883` (configurable).
    -   Receives sensor data in JSON format.
    -   Handles potential JSONDecodeErrors and attempts to fix common formatting issues.
    -   Validates incoming data structure to ensure all expected fields are present.
    -   Appends valid sensor data to `sensor_data.csv`, including a timestamp.
    -   Uses logging for information, warnings, and errors.

-   **`sensor_data.csv`**:
    -   CSV file storing sensor data.
    -   Columns: `timestamp`, `soil_moisture`, `soil_nitrogen`, `soil_phosphorus`, `soil_potassium`, `soil_temperature`, `soil_humidity`, `soil_ph`, `air_temperature`, `air_humidity`.
    -   Data is appended to this file by `mqtt_listener.py`.
    -   Read by `streamlit_app.py` for visualization and analysis.

-   **`streamlit_app.py`**:
    -   Streamlit application for visualizing sensor data from `sensor_data.csv`.
    -   Provides a multi-page dashboard with:
        -   Real-time dashboard with gauges and metric displays.
        -   Detailed analysis page with statistical summaries, time series, correlations, and distributions.
        -   Historical data exploration with date range filtering, aggregation, and export options.
        -   About page with project information.
    -   Includes features like:
        -   Data filtering by timeframe.
        -   Auto-refresh option for real-time updates.
        -   Interactive charts using Plotly.
        -   Data export to CSV and JSON.
        -   Responsive layout and custom CSS styling.


This project provides a comprehensive solution for monitoring agricultural sensor data, from data collection and storage to interactive visualization and analysis, enabling users to gain valuable insights into field conditions.
