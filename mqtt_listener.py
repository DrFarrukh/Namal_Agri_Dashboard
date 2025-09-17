import paho.mqtt.client as mqtt
import csv
import time
import json
import logging
import re
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MQTT Broker Details
broker_address = "localhost"  # Change this to your MQTT broker address (10.0.0.164)
port = 1883
topic = "agri_sensor/data"

# File Details
csv_file = "sensor_data.csv"
json_file = "sensor_data.json"
fieldnames = ["timestamp", "mac_address", "crop_number", "date", "time", "soil_moisture", "soil_nitrogen", "soil_phosphorus", 
              "soil_potassium", "soil_temperature", "soil_conductivity", "soil_ph", "air_temperature", "air_humidity"]

# Initialize CSV file with header if it doesn't exist
try:
    with open(csv_file, 'x', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
except FileExistsError:
    pass  # File already exists, continue

def on_connect(client, userdata, flags, rc):
    logging.info(f"Connected with result code {rc}")
    client.subscribe(topic)

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode('utf-8').strip()
        logging.info(f"Received message: {payload_str}")
        
        import ast
        try:
            # Try to parse the JSON directly
            data = json.loads(payload_str)
            logging.info("JSON parsed successfully (single decode)")
        except json.JSONDecodeError as e:
            logging.warning(f"First JSON decode failed: {str(e)}. Attempting second decode (double-encoded payload)...")
            try:
                data = json.loads(json.loads(payload_str))
                logging.info("JSON parsed successfully (double decode)")
            except Exception as e2:
                logging.warning(f"Double-decoding also failed: {str(e2)}. Attempting to unescape and decode...")
                try:
                    unescaped = ast.literal_eval(f"'{payload_str}'")
                    data = json.loads(unescaped)
                    logging.info("JSON parsed successfully (after unescape)")
                except Exception as e3:
                    logging.error(f"Unescape and decode also failed: {str(e3)}")
                    logging.error(f"Raw payload bytes: {msg.payload}")
                    return
        
        # Create a normalized data dictionary with lowercase keys
        normalized_data = {}
        for key, value in data.items():
            normalized_key = key.lower()
            normalized_data[normalized_key] = value
        
        # Add timestamp if not present
        if "timestamp" not in normalized_data:
            normalized_data["timestamp"] = time.time()
        
        # Ensure all fields are present in the data
        for field in fieldnames:
            if field not in normalized_data:
                normalized_data[field] = None
        
        # Write to CSV file
        with open(csv_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(normalized_data)
        
        # Save to JSON file
        save_to_json(normalized_data)
        
        logging.info(f"Data saved to CSV and JSON: {normalized_data}")
    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())

def save_to_json(data_entry):
    """Save data to a JSON file, appending to an array or creating new file if needed"""
    try:
        # Load existing data if file exists
        if os.path.exists(json_file) and os.path.getsize(json_file) > 0:
            with open(json_file, 'r') as f:
                try:
                    all_data = json.load(f)
                    if not isinstance(all_data, list):
                        all_data = [all_data]  # Convert to list if not already
                except json.JSONDecodeError:
                    logging.warning(f"Could not decode existing JSON file. Creating new file.")
                    all_data = []
        else:
            all_data = []
        
        # Append new data
        all_data.append(data_entry)
        
        # Write back to file
        with open(json_file, 'w') as f:
            json.dump(all_data, f, indent=2)
        
    except Exception as e:
        logging.error(f"Error saving to JSON: {str(e)}")

# Connect to MQTT broker
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(broker_address, port, 60)
    logging.info(f"Connecting to broker at {broker_address}:{port}")
    client.loop_forever()
except Exception as e:
    logging.error(f"Failed to connect to broker: {str(e)}")
