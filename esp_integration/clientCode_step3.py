from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from threading import Thread, Event
import os
import sys

app = Flask(__name__)

def step1(sunrise_time, sunset_time):
    def time_to_hours(time_str):
        hours, minutes = map(int, time_str[:-2].split(':'))
        if time_str.endswith('PM') and hours != 12:
            hours += 12
        elif time_str.endswith('AM') and hours == 12:
            hours = 0
        return hours + minutes / 60

    def hours_to_time_str(hours):
        time = datetime(2000, 1, 1) + timedelta(hours=hours)
        return time.strftime("%I:%M %p")

    def generate_cct_curve(sunrise, sunset, reference_data):
        sunrise_hour = time_to_hours(sunrise)
        sunset_hour = time_to_hours(sunset)

        # Load reference data
        data = pd.read_csv(reference_data)
        time = np.array([time_to_hours(t) for t in data['Time']])
        cct = np.array(data['Color Temperature (K)'])

        # Define the Gaussian function
        def gaussian(t, A, mu, sigma):
            return A * np.exp(-((t - mu) ** 2) / (2 * sigma ** 2))

        # Fit the Gaussian to the data
        # Initial guess: A (max CCT), mu (mean time), sigma (standard deviation)
        initial_guess = [max(cct), np.mean(time), 1]
        popt, _ = curve_fit(gaussian, time, cct, p0=initial_guess)

        # Generate time array at 5-minute intervals
        t_smooth = np.arange(0, 24, 5/60)

        # Calculate the fitted values
        cct_fit = gaussian(t_smooth, *popt)

        # Adjust CCT values based on sunrise and sunset
        cct_fit = np.where((t_smooth < sunrise_hour) | (t_smooth > sunset_hour), 2700, cct_fit)
        cct_fit = np.clip(cct_fit, 2700, 6500)

        # Calculate brightness (normalized between 0 and 1)
        brightness = (cct_fit - 2700) / (6500 - 2700)
        brightness = np.clip(brightness, 0, 1)

        return t_smooth, cct_fit, brightness

        reference_data = 'input_data.csv'  # This should contain a 'Time' and 'Color Temperature (K)' column

        t, cct, brightness = generate_cct_curve(sunrise_time, sunset_time, reference_data)

        # Create a DataFrame with time in AM/PM format
        df = pd.DataFrame({
            'Time': [hours_to_time_str(h) for h in t],
            'Color Temperature (K)': np.round(cct).astype(int),
            'Brightness': np.round(brightness, 2)  # Rounded to two decimal places
        })

        # Save to CSV
        df.to_csv('generated_circadian_cct_brightness.csv', index=False)

        # Plot the curves
        plt.figure(figsize=(12, 6))
        plt.plot(t, cct, label='Color Temperature (K)', color='blue')
        plt.plot(t, brightness * (6500), label='Brightness', color='yellow', linestyle='--')  # Scale brightness for better visualization
        plt.xlabel('Time (hours)')
        plt.ylabel('Value')
        plt.title(f'Circadian Rhythm: Color Temperature and Brightness vs Time\nSunrise: {sunrise_time}, Sunset: {sunset_time}')
        plt.xticks(range(0, 25, 2))
        plt.legend()
        plt.grid(True)
        plt.savefig('generated_circadian_cct_brightness.png')
        plt.close()

        print("CCT curve with brightness generated. Results saved to 'generated_circadian_cct_brightness.csv' and 'generated_circadian_cct_brightness.png'.")

def step2():
    cie_data = pd.read_csv('CIE_xyz_1931_2deg.csv', header=None)

    # Extract wavelength and color matching functions data
    wavelengths = cie_data.iloc[:, 0].values
    x_bar = cie_data.iloc[:, 1].values
    y_bar = cie_data.iloc[:, 2].values
    z_bar = cie_data.iloc[:, 3].values

    # Standard RGB transformation matrix from XYZ (sRGB color space)
    xyz_to_rgb_matrix = np.array([
        [3.2406, -1.5372, -0.4986],
        [-0.9999, 1.6758, 0.0459],
        [0.0557, -0.2040, 1.0570]
    ])

    def get_warmness_matrix(warmness_level):
        """
        Creates a warmness matrix based on user input level (0.0 to 1.0)
        Higher values make colors warmer by emphasizing reds and reducing blues
        """
        return np.array([
            [1 + (0.3 * warmness_level), 0, 0],  # Increased red enhancement
            [0, 1 + (0.3 * warmness_level), 0],  # Slightly increase green
            [0, 0, 1 - (0.4 * warmness_level)]   # More blue reduction
        ])

    class ColorTemperatureConverter:
        def __init__(self, cct, warmness=0.7):
            self.cct = cct
            self.warmness = max(0.0, min(1.0, warmness))

        def planck_law(self, wavelength):
            h = 6.62607015e-34
            c = 2.99792458e8
            k = 1.380649e-23
            l = wavelength * 1e-9
            return (2 * h * c ** 2) / (l ** 5) * (1 / (np.exp(h * c / (l * k * self.cct)) - 1))

        def cct_to_xyz(self):
            spectral_radiance = self.planck_law(wavelengths)
            X = np.trapz(spectral_radiance * x_bar, wavelengths)
            Y = np.trapz(spectral_radiance * y_bar, wavelengths)
            Z = np.trapz(spectral_radiance * z_bar, wavelengths)
            
            XYZ = np.array([X, Y, Z])
            XYZ /= np.max(XYZ)
            return XYZ

        def xyz_to_rgb(self, xyz):
            print("Input XYZ values:", xyz)
            
            # Apply warmness transformation first
            warmness_matrix = get_warmness_matrix(self.warmness)
            modified_matrix = np.dot(warmness_matrix, xyz_to_rgb_matrix)
            
            # Convert to RGB
            rgb = np.dot(modified_matrix, xyz)
            print("After matrix multiplication:", rgb)
            
            # Normalize each channel independently
            for i in range(3):
                if rgb[i] < 0:
                    rgb[i] = abs(rgb[i])
            
            # Scale to ensure proper range
            max_val = np.max(rgb)
            if max_val > 0:
                rgb = rgb / max_val
            
            rgb = (rgb * 255).astype(int)
            print("Final RGB values:", rgb)
            
            return rgb

        def get_rgb(self):
            xyz = self.cct_to_xyz()
            return self.xyz_to_rgb(xyz)

    def load_lookup_table(filename):
        df = pd.read_csv(filename)
        return df['Color Temperature (K)'].values, df['Brightness'].values

    def save_rgb_to_csv(cct_values,brightness_values, output_filename):
        rgb_values = []

        for cct,brightness in zip(cct_values, brightness_values):
            converter = ColorTemperatureConverter(cct, warmness=0.9)
            rgb = converter.get_rgb()
            rgb_values.append((cct, *rgb, brightness))

        # Create a DataFrame and save to CSV
        rgb_df = pd.DataFrame(rgb_values, columns=['CCT (K)', 'R', 'G', 'B', 'Brightness'])
        rgb_df.to_csv(output_filename, index=False)
        print(f"RGB values saved to {output_filename}")
    # Load the color temperature values from the CSV
    cct_values, brightness_values = load_lookup_table('generated_circadian_cct_brightness.csv')
    
    # Save the RGB values to a new CSV
    save_rgb_to_csv(cct_values,brightness_values, 'rgb_values.csv')

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
