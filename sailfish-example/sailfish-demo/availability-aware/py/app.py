from flask import Flask, jsonify
import random
from prometheus_client import start_http_server, Gauge

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

@app.route('/')
def home():
    return "Azure Cluster Availability Dummy App"

@app.route('/check_availability')
def check_availability():
    availability_data = {}
    for region in azure_regions:
        # Randomly generate availability percentage for the region
        availability_percentage = random.uniform(0, 100)
        availability_data[region] = availability_percentage
        # Update Prometheus metric
        availability_metric.labels(region).set(availability_percentage)
    return jsonify(availability_data)

if __name__ == '__main__':
    # Start up the Prometheus server
    start_http_server(8000)
    app.run(host='0.0.0.0', port=5000)
