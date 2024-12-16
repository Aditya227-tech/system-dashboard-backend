from flask import Flask, jsonify
from flask_cors import CORS
import psutil
import platform
import requests
import GPUtil
import time
import socket
import json
from flask import render_template
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

def get_ip_location():
    try:
        response = requests.get('https://ipapi.co/json/')
        if response.status_code == 200:
            data = response.json()
            return {
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'country': data.get('country_name', 'Unknown')
            }
    except Exception as e:
        print(f"Error fetching location: {e}")
    return {'city': 'Unknown', 'region': 'Unknown', 'country': 'Unknown'}

@app.route('/')
def serve_frontend():
    return render_template('index.html')

@app.route('/system-info')
def get_system_info():
    # Current Time
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")

    # Python Version
    python_version = platform.python_version()

    # Battery Status
    battery = psutil.sensors_battery()
    battery_info = {
        'percent': battery.percent if battery else None,
        'power_plugged': battery.power_plugged if battery else None
    }

    # CPU Information
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_temp = None
    try:
        cpu_temp = psutil.sensors_temperatures().get('coretemp', [{}])[0].current
    except Exception:
        pass

    # RAM Usage
    ram = psutil.virtual_memory()
    ram_usage = {
        'total': ram.total / (1024 * 1024 * 1024),  # Convert to GB
        'used': ram.used / (1024 * 1024 * 1024),
        'percent': ram.percent
    }

    # GPU Usage
    gpu_usage = None
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            gpu_usage = {
                'name': gpu.name,
                'load': gpu.load * 100,
                'memory_used': gpu.memoryUsed,
                'memory_total': gpu.memoryTotal
            }
    except Exception:
        pass

    # IP Location
    location = get_ip_location()

    # Combine all system information
    system_info = {
        'current_time': current_time,
        'python_version': python_version,
        'battery': battery_info,
        'cpu': {
            'usage': cpu_usage,
            'temperature': cpu_temp
        },
        'ram': ram_usage,
        'gpu': gpu_usage,
        'location': location
    }

    return jsonify(system_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)