# Namal Agri Dashboard

This project is a real-time dashboard for monitoring agricultural sensor data. It uses an MQTT listener to collect data from IoT devices and a Flask-based web application to visualize it.

## Features

-   Real-time sensor data visualization
-   Modern, responsive user interface
-   Interactive charts for various sensor parameters
-   Containerized with Docker for easy deployment

## Technologies Used

-   **Backend**: Flask, Gunicorn, Paho-MQTT
-   **Frontend**: HTML, CSS, JavaScript, Chart.js
-   **Containerization**: Docker, Docker Compose

## Getting Started

To get the dashboard running on a new machine, follow these steps:

### Prerequisites

-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)

### Setup & Run

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd Namal_Agri_Dashboard
    ```

2.  **Configure the Platform (if necessary):**

    The `docker-compose.yml` file is pre-configured to run on a Raspberry Pi 4 (`linux/arm64`). If you are running this on a different architecture (e.g., a standard x86 laptop), open `docker-compose.yml` and change the `platform` for each service:

    -   For x86/amd64, change `platform: linux/arm64` to `platform: linux/amd64`.

3.  **Build and Run with Docker Compose:**

    In the project's root directory, run the following command:

    ```bash
    docker-compose up --build -d
    ```

    This command will build the Docker images and start the dashboard, MQTT listener, and MQTT broker in the background.

4.  **Access the Dashboard:**

    Open your web browser and navigate to [http://localhost:5000](http://localhost:5000). You should see the agricultural dashboard, which will update in real-time as new sensor data is received.

### Stopping the Application

To stop all the running services, use the following command:

```bash
docker-compose down
```
