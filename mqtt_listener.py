import paho.mqtt.client as mqtt
import csv
import time
import json
import logging
import re
import os
from datetime import datetime

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

# Data validation ranges - based on realistic agricultural sensor values
VALIDATION_RANGES = {
    "soil_moisture": {"min": 0, "max": 100, "type": "float", "unit": "%"},
    "soil_nitrogen": {"min": 0, "max": 200, "type": "float", "unit": "mg/kg"},
    "soil_phosphorus": {"min": 0, "max": 150, "type": "float", "unit": "mg/kg"},
    "soil_potassium": {"min": 0, "max": 500, "type": "float", "unit": "mg/kg"},
    "soil_temperature": {"min": -10, "max": 60, "type": "float", "unit": "°C"},
    "soil_conductivity": {"min": 0, "max": 200, "type": "float", "unit": "mS/cm"},
    "soil_ph": {"min": 3.0, "max": 10.0, "type": "float", "unit": "pH"},
    "air_temperature": {"min": -40, "max": 60, "type": "float", "unit": "°C"},
    "air_humidity": {"min": 0, "max": 100, "type": "float", "unit": "%"},
    "crop_number": {"min": 0, "max": 100, "type": "int", "unit": ""}
}

def validate_value(field_name, value, ranges=VALIDATION_RANGES):
    """
    Validate sensor value against defined ranges.
    Returns: (is_valid, corrected_value, error_message)
    """
    if field_name not in ranges:
        return True, value, None  # Field not in validation list, accept as-is
    
    if value is None or value == "":
        return True, None, None  # Allow None/empty values
    
    try:
        # Convert to appropriate type
        range_config = ranges[field_name]
        if range_config["type"] == "int":
            value = int(float(value))  # Convert via float first to handle "10.0" strings
        else:
            value = float(value)
        
        # Check range
        if value < range_config["min"] or value > range_config["max"]:
            error_msg = f"{field_name} value {value} out of range [{range_config['min']}, {range_config['max']}] {range_config['unit']}"
            return False, None, error_msg
        
        return True, value, None
    
    except (ValueError, TypeError) as e:
        error_msg = f"{field_name} has invalid type: {value} ({type(value).__name__})"
        return False, None, error_msg

def validate_mac_address(mac_address):
    """Validate MAC address format"""
    if mac_address is None or mac_address == "":
        return True, None, None
    
    # Pattern: XX:XX:XX:XX:XX:XX where X is hex digit
    pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
    if re.match(pattern, str(mac_address)):
        return True, mac_address.upper(), None
    else:
        return False, None, f"Invalid MAC address format: {mac_address}"

def validate_sensor_data(data):
    """
    Validate all sensor data fields.
    Returns: (is_valid, validated_data, errors)
    """
    validated_data = {}
    errors = []
    
    # Validate MAC address
    is_valid, mac_value, error = validate_mac_address(data.get("mac_address"))
    if not is_valid:
        errors.append(error)
        return False, None, errors
    validated_data["mac_address"] = mac_value
    
    # Validate numeric fields
    for field_name in VALIDATION_RANGES.keys():
        value = data.get(field_name)
        is_valid, validated_value, error = validate_value(field_name, value)
        
        if not is_valid:
            errors.append(error)
        else:
            validated_data[field_name] = validated_value
    
    # Copy non-validated fields (timestamp, date, time)
    validated_data["timestamp"] = data.get("timestamp")
    validated_data["date"] = data.get("date")
    validated_data["time"] = data.get("time")
    
    # Return validation result
    if errors:
        return False, validated_data, errors
    else:
        return True, validated_data, []

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
        
        # Validate sensor data
        is_valid, validated_data, errors = validate_sensor_data(normalized_data)
        
        if not is_valid:
            logging.error(f"❌ DATA VALIDATION FAILED - Data rejected and NOT saved!")
            for error in errors:
                logging.error(f"  - {error}")
            logging.error(f"  Rejected data: {normalized_data}")
            return  # Do not save invalid data
        
        logging.info("✓ Data validation passed")
        
        # Ensure all fields are present in the validated data
        for field in fieldnames:
            if field not in validated_data:
                validated_data[field] = None
        
        # Write to CSV file
        with open(csv_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(validated_data)
        
        # Save to JSON file
        save_to_json(validated_data)
        
        logging.info(f"Data saved to CSV and JSON: {validated_data}")
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
