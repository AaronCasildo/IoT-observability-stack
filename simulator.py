#!/usr/bin/env python3
"""
IoT Sensor Data Simulator for InfluxDB

This script simulates temperature and humidity sensors, sending data to InfluxDB
at regular intervals. Useful for testing and demonstrating the IoT observability stack.

Author: Aaron Casildo Rubalcava
Institution: TECNM / Instituto Tecnológico de Tijuana
Subject: Sistemas Programables
Year: 2025
"""

from datetime import datetime
import random
import time
import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


# --- CONFIGURATION ---
# These can be overridden by environment variables
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "SistemasProgramables")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "datos")

# Sensor configuration
SENSOR_LOCATION = os.getenv("SENSOR_LOCATION", "laboratorio")
TEMP_MIN = float(os.getenv("TEMP_MIN", "18.0"))
TEMP_MAX = float(os.getenv("TEMP_MAX", "30.0"))
HUMIDITY_MIN = float(os.getenv("HUMIDITY_MIN", "40.0"))
HUMIDITY_MAX = float(os.getenv("HUMIDITY_MAX", "70.0"))
SEND_INTERVAL = int(os.getenv("SEND_INTERVAL", "5"))  # seconds


def validate_configuration():
    """Validate that all required configuration is present."""
    if not INFLUXDB_TOKEN:
        raise ValueError(
            "INFLUXDB_TOKEN not set. Please set it via environment variable "
            "or modify the script directly."
        )


def create_client():
    """Create and return an InfluxDB client."""
    client = InfluxDBClient(
        url=INFLUXDB_URL,
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG
    )
    return client


def generate_sensor_data():
    """Generate simulated sensor readings."""
    temperatura = round(random.uniform(TEMP_MIN, TEMP_MAX), 2)
    humedad = round(random.uniform(HUMIDITY_MIN, HUMIDITY_MAX), 2)
    return temperatura, humedad


def send_data(write_api, temperatura, humedad):
    """Send sensor data to InfluxDB."""
    punto = (
        Point("ambiente")
        .tag("ubicacion", SENSOR_LOCATION)
        .field("temperatura", temperatura)
        .field("humedad", humedad)
        .time(datetime.utcnow(), WritePrecision.NS)
    )
    write_api.write(bucket=INFLUXDB_BUCKET, record=punto)


def main():
    """Main simulator loop."""
    try:
        validate_configuration()
        client = create_client()
        write_api = client.write_api(write_options=SYNCHRONOUS)
        
        print("=" * 60)
        print("IoT SENSOR DATA SIMULATOR")
        print("=" * 60)
        print(f"InfluxDB URL: {INFLUXDB_URL}")
        print(f"Organization: {INFLUXDB_ORG}")
        print(f"Bucket: {INFLUXDB_BUCKET}")
        print(f"Location: {SENSOR_LOCATION}")
        print(f"Send Interval: {SEND_INTERVAL} seconds")
        print(f"Temperature Range: {TEMP_MIN}°C - {TEMP_MAX}°C")
        print(f"Humidity Range: {HUMIDITY_MIN}% - {HUMIDITY_MAX}%")
        print("=" * 60)
        print("Simulator started. Press Ctrl+C to stop.\n")
        
        iteration = 0
        while True:
            iteration += 1
            temperatura, humedad = generate_sensor_data()
            
            try:
                send_data(write_api, temperatura, humedad)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"[{timestamp}] #{iteration} - "
                    f"Temp: {temperatura}°C | Humidity: {humedad}%"
                )
            except Exception as e:
                print(f"Error sending data: {e}")
            
            time.sleep(SEND_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Simulator stopped by user.")
        print(f"Total iterations: {iteration}")
        print("=" * 60)
    except ValueError as e:
        print(f"Configuration Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        exit(1)
    finally:
        if 'client' in locals():
            client.close()


if __name__ == "__main__":
    main()
