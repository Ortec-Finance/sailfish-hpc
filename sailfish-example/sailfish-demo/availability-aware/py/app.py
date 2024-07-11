from flask import Flask, jsonify
import random
from prometheus_client import start_http_server, Gauge
import time
import threading

app = Flask(__name__)

# Prometheus metrics setup
availability_metric = Gauge('azure_region_availability', 'Percentage availability of Azure regions', ['region'])

# Dummy data for Azure regions
azure_regions = [
    'eastus', 'westus', 'centralus', 'eastasia', 'southeastasia',
    'northeurope', 'westeurope', 'japaneast', 'japanwest', 'brazilsouth',
    'australiaeast', 'australiasoutheast', 'southindia', 'centralindia', 'westindia',
    'canadacentral', 'canadaeast', 'uksouth', 'ukwest', 'koreacentral', 'koreasouth'
]

# Initialize each region with a starting random availability
current_availability = {region: random.uniform(10, 50) for region in azure_regions}

@app.route('/')
def home():
    return "Azure Cluster Availability Dummy App"

@app.route('/check_availability')
def check_availability():
    return jsonify(generate_metrics())

def generate_metrics():
    availability_data = {}
    for region in azure_regions:
        # Adjust availability percentage by a small random amount
        change = random.uniform(-5, 5)  # Change up to 0.5% up or down
        new_availability = current_availability[region] + change
        # Ensure availability stays within 0 to 100%
        new_availability = max(0, min(50, new_availability))
        current_availability[region] = new_availability
        availability_data[region] = new_availability
        # Update Prometheus metric
        availability_metric.labels(region).set(new_availability)
    return availability_data

def refresh_availability():
    while True:
        generate_metrics()
        time.sleep(5)  # Refresh every 5 seconds

if __name__ == '__main__':
    # Create a new thread for running the refresh_availability function
    refresh_thread = threading.Thread(target=refresh_availability)
    # Set the thread as a daemon so it runs in the background
    refresh_thread.daemon = True
    # Start the thread
    refresh_thread.start()
    # Start up the Prometheus server
    start_http_server(8000)
    app.run(host='0.0.0.0', port=5000)
