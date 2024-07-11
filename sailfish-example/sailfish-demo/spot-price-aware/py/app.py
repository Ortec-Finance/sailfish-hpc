from flask import Flask, jsonify
import random
from prometheus_client import start_http_server, Gauge
import time
import threading

app = Flask(__name__)

# Prometheus metrics setup
spot_metric = Gauge('azure_spot_price', 'Cost of Spot price of Azure regions', ['region'])

# Dummy data for Azure regions
azure_regions = [
    'eastus', 'westus', 'centralus', 'eastasia', 'southeastasia',
    'northeurope', 'westeurope', 'japaneast', 'japanwest', 'brazilsouth',
    'australiaeast', 'australiasoutheast', 'southindia', 'centralindia', 'westindia',
    'canadacentral', 'canadaeast', 'uksouth', 'ukwest', 'koreacentral', 'koreasouth'
]

# Initialize each region with a starting random spot price
current_spot = {region: round(random.uniform(0.1, 1), 2) for region in azure_regions}

@app.route('/')
def home():
    return "Azure Cluster Spot Price Dummy App"

@app.route('/check_spot_price')
def check_spot_price():
    return jsonify(generate_metrics())

def generate_metrics():
    spot_data = {}
    for region in azure_regions:
        # Adjust spot price by a small random amount, allowing decrease and increase
        change = random.uniform(-0.05, 0.05)  # Change up to 0.05 up or down
        new_spot = current_spot[region] + change
        # Ensure spot price stays within 0.1 to 1
        new_spot = max(0.1, min(1, new_spot))
        # Format to two decimal places
        new_spot = round(new_spot, 2)
        current_spot[region] = new_spot
        spot_data[region] = new_spot
        # Update Prometheus metric
        spot_metric.labels(region).set(new_spot)
    return spot_data

def refresh_spot():
    while True:
        generate_metrics()
        time.sleep(5)  # Refresh every 5 seconds

if __name__ == '__main__':
    # Create a new thread for running the refresh_spot function
    refresh_thread = threading.Thread(target=refresh_spot)
    # Set the thread as a daemon so it runs in the background
    refresh_thread.daemon = True
    # Start the thread
    refresh_thread.start()
    # Start up the Prometheus server
    start_http_server(8000)
    app.run(host='0.0.0.0', port=5000)
