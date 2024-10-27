from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from threading import Thread, Event
import os
import sys

app = Flask(__name__)


# Path to your CSV file
csv_file = 'rgb_values.csv'
last_manual_input_time = None
testing_mode = False  # Flag to check if we are in testing mode
stop_threads = Event()  # Event to stop running threads
# ESP32 URL (replace with the actual IP of ESP32 on the same network)
ESP32_URL = "http://192.168.63.89/set_color"

# Load CSV data
data = pd.read_csv(csv_file)

# Function to send data to ESP32
def send_to_esp32(r, g, b, brightness):
    payload = {'R': r, 'G': g, 'B': b, 'Brightness': brightness}
    try:
        response = requests.post(ESP32_URL, data=payload)
        if response.status_code == 200:
            print("Command sent to ESP32 successfully.")
        else:
            print("Failed to send command to ESP32.")
    except Exception as e:
        print(f"Error: {e}")

# Function to get current color values based on time
def get_current_values():
    current_time = datetime.now().strftime('%H:%M')
    # Match the current time to the nearest 5-minute interval in the CSV
    row = data.iloc[int(datetime.now().strftime('%H')) * 12 + int(datetime.now().strftime('%M')) // 5]
    return int(row['R']), int(row['G']), int(row['B']), (float(row['Brightness']) + 0.2)

# Flask route to show web interface
@app.route('/')
def index():
    return render_template('index.html')

# Flask route to send manual commands
@app.route('/set_color', methods=['POST'])
def set_color():
    global last_manual_input_time
    r = int(request.form['r'])
    g = int(request.form['g'])
    b = int(request.form['b'])
    brightness = float(request.form['brightness'])
    last_manual_input_time = datetime.now()
    send_to_esp32(r, g, b, brightness)
    return redirect(url_for('index'))

# Background task that keeps the ESP32 synchronized with the CSV file
def sync_with_csv():
    global last_manual_input_time, testing_mode, stop_threads
    last_values = None
    while not stop_threads.is_set():
        if not testing_mode:
            current_time = datetime.now()
            
            # Check if more than 20 seconds have passed since the last manual input
            if last_manual_input_time is None or (current_time - last_manual_input_time) > timedelta(seconds=20):
                current_values = get_current_values()
                if last_values != current_values:
                    # Override manual input with CSV data after 20 seconds
                    send_to_esp32(*current_values)
                    last_values = current_values
        time.sleep(20)  # Check every 20 seconds for efficiency

# Route to trigger testing all CSV values
@app.route('/test_csv')
def test_csv():
    global testing_mode, stop_threads
    # Enable testing mode
    testing_mode = True
    stop_threads.clear()  # Ensure the sync thread continues after testing

    # Run through all values in the CSV
    def run_test():
        for index, row in data.iterrows():
            if stop_threads.is_set():
                return
            r, g, b, brightness = int(row['R']), int(row['G']), int(row['B']), min(1, float(row['Brightness']+0.2))
            send_to_esp32(r, g, b, brightness)
            print(f"Testing row {index}: R={r}, G={g}, B={b}, Brightness={brightness}")
            time.sleep(0.001)  # Short delay for quick testing
        
        # Test completed, return to normal routine
        global testing_mode
        testing_mode = False
        print("Test completed. Returning to normal operation.")
        last_manual_input_time = None  # Ensure it goes back to CSV syncing

    # Start the test in a separate thread so it doesn't block the server
    Thread(target=run_test).start()

    return "Testing CSV values. Please wait..."

# Route to return to normal operation (kill all threads and start sync_with_csv again)
@app.route('/return_to_normal')
def return_to_normal():
    global testing_mode, stop_threads
    testing_mode = False  # Reset the testing mode flag
    stop_threads.set()  # Stop all ongoing threads by setting the flag
    time.sleep(1)  # Give some time for threads to terminate

    # Start the sync_with_csv task again
    stop_threads.clear()
    Thread(target=sync_with_csv, daemon=True).start()
    
    print("Returning to normal operation.")
    return "Returning to normal operation.", 200

# Route to restart the server
@app.route('/restart_server')
def restart_server():
    def restart():
        print("Server restarting...")
        os.execv(sys.executable, ['python'] + [" ", "c:/Users/Unnath Ch/Documents/GitHub/eyantra/esp_integration/clientCode.py"])
    
    # Restart in a separate thread to allow the response to be sent back first
    Thread(target=restart).start()
    
    return "Server restarting...", 200

if __name__ == '__main__':
    # Start the background CSV sync task
    Thread(target=sync_with_csv, daemon=True).start()

    # Run Flask app
    app.run(host='0.0.0.0', port=5000)
