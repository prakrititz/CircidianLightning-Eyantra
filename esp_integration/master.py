# app.py
from flask import Flask, request, render_template, redirect, url_for, jsonify
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from threading import Thread, Event
import os
import sys
import pytz
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
MAX_COLOR_TEMP = 6500
MIN_COLOR_TEMP = 2700
AMPLITUDE = MAX_COLOR_TEMP-MIN_COLOR_TEMP
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


    def generate_cct_curve_sinusoidal(sunrise, sunset, reference_data):
        sunrise_hour = time_to_hours(sunrise)
        sunset_hour = time_to_hours(sunset)

        # Calculate midday point and scale factor
        midday = sunrise_hour + (sunset_hour - sunrise_hour) / 2
        daylight_duration = sunset_hour - sunrise_hour
        scale_factor = 12 / daylight_duration  # Normalize to 12-hour period

        t_smooth = np.arange(0, 24, 5 / 60)
        transition_period = 0.5  # 30 minutes transition

        def sinusoidal(t):
            # Scale time around midday
            scaled_t = (t - midday) * scale_factor
            # Sine wave scaled to CCT range (2700K to 6500K)
            return 2700 + 3800 * (1 + np.cos(np.pi * scaled_t / 6)) / 2

        cct_fit = sinusoidal(t_smooth)

        # Smooth transitions
        sunrise_mask = (t_smooth >= (sunrise_hour - transition_period)) & (t_smooth <= sunrise_hour)
        sunset_mask = (t_smooth >= sunset_hour) & (t_smooth <= (sunset_hour + transition_period))

        sunrise_factor = (t_smooth[sunrise_mask] - (sunrise_hour - transition_period)) / transition_period
        sunset_factor = 1 - (t_smooth[sunset_mask] - sunset_hour) / transition_period

        cct_fit[sunrise_mask] = 2700 + (cct_fit[sunrise_mask] - 2700) * sunrise_factor
        cct_fit[sunset_mask] = 2700 + (cct_fit[sunset_mask] - 2700) * sunset_factor
        cct_fit[t_smooth < (sunrise_hour - transition_period)] = 2700
        cct_fit[t_smooth > (sunset_hour + transition_period)] = 2700

        cct_fit = np.clip(cct_fit, 2700, 6500)

        brightness = (cct_fit - 2700) / (6500 - 2700)
        brightness = np.clip(brightness, 0, 1)

        return t_smooth, cct_fit, brightness
    
    def generate_cct_curve_parabolic(sunrise, sunset, reference_data):
        sunrise_hour = time_to_hours(sunrise)
        sunset_hour = time_to_hours(sunset)
        
        # Calculate midday point
        midday = sunrise_hour + (sunset_hour - sunrise_hour) / 2
        daylight_duration = sunset_hour - sunrise_hour
        
        t_smooth = np.arange(0, 24, 5/60)
        transition_period = 0.5  # 30 minutes transition
        
        def parabolic(t):
            # Parabola scaled to CCT range (MIN_COLOR_TEMPK to MAX_COLOR_TEMPK)
            a = -AMPLITUDE / ((daylight_duration/2)**2)  # Coefficient to reach MAX_COLOR_TEMPK at peak
            return MAX_COLOR_TEMP + a * (t - midday)**2
        
        cct_fit = parabolic(t_smooth)
        
        # Smooth transitions
        sunrise_mask = (t_smooth >= (sunrise_hour - transition_period)) & (t_smooth <= sunrise_hour)
        sunset_mask = (t_smooth >= sunset_hour) & (t_smooth <= (sunset_hour + transition_period))
        
        sunrise_factor = (t_smooth[sunrise_mask] - (sunrise_hour - transition_period)) / transition_period
        sunset_factor = 1 - (t_smooth[sunset_mask] - sunset_hour) / transition_period
        
        cct_fit[sunrise_mask] = MIN_COLOR_TEMP + (cct_fit[sunrise_mask] - MIN_COLOR_TEMP) * sunrise_factor
        cct_fit[sunset_mask] = MIN_COLOR_TEMP + (cct_fit[sunset_mask] - MIN_COLOR_TEMP) * sunset_factor
        cct_fit[t_smooth < (sunrise_hour - transition_period)] = MIN_COLOR_TEMP
        cct_fit[t_smooth > (sunset_hour + transition_period)] = MIN_COLOR_TEMP
        
        cct_fit = np.clip(cct_fit, MIN_COLOR_TEMP, MAX_COLOR_TEMP)
        
        brightness = (cct_fit - MIN_COLOR_TEMP) / (MAX_COLOR_TEMP - MIN_COLOR_TEMP)
        brightness = np.clip(brightness, 0, 1)
        
        return t_smooth, cct_fit, brightness

    reference_data = 'input_data.csv'  # This should contain a 'Time' and 'Color Temperature (K)' column

    t, cct, brightness = generate_cct_curve_parabolic(sunrise_time, sunset_time, reference_data)

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


def step2(mode):
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
    
    #TODO: Implement weather based matrices, based on ma'ams suggestion
    def get_hospital_matrix():
        """
        Creates a matrix optimized for hospital environments with enhanced green tones
        for a calming and clinical atmosphere
        """
        return np.array([
            [0.7, 0, 0],      # Reduce red
            [0, 1.4, 0],      # Enhance green
            [0, 0, 0.7]       # Normal blue
        ])

    def get_office_focus_matrix():
        """
        Creates a matrix optimized for office focus areas with enhanced blue tones
        to promote alertness and concentration
        """
        return np.array([
            [0.8, 0, 0],      # Slightly reduce red
            [0, 1.0, 0],      # Normal green
            [0, 0, 1.4]       # Enhance blue
        ])

    def get_cafe_matrix():
        """
        Creates a matrix optimized for cafe environments with enhanced warm tones
        for a cozy and inviting atmosphere
        """
        return np.array([
            [1.3, 0, 0],      # Enhance red
            [0, 1.1, 0],      # Slightly enhance green
            [0, 0, 0.7]       # Reduce blue
        ])

    class ColorTemperatureConverter:
        def __init__(self, cct, warmness=0.7):
            self.cct = cct
            self.warmness = max(0.0, min(1.5, warmness))

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

        def xyz_to_rgb(self, xyz, mode ='none'):
            print('MODE IS', mode)
            print("Input XYZ values:", xyz)
            transform = None
            if mode == 'warm' or mode =='none':
                transform = get_warmness_matrix(self.warmness)
            elif mode == 'hospital':
                transform = get_hospital_matrix()
                print('Doing hospital matrix')
            elif mode == 'office':
                transform = get_office_focus_matrix()
            elif mode == 'cafe':
                transform = get_cafe_matrix()
            else:
                raise ValueError("Invalid mode. Choose from 'None', 'warmness', 'hospital', 'office_focus', or 'cafe'.")
            # Apply warmness transformation first
            # transform = get_warmness_matrix(self.warmness)
            modified_matrix = np.dot(transform, xyz_to_rgb_matrix)
            
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

        def get_rgb(self, mode='none'):
            xyz = self.cct_to_xyz()
            return self.xyz_to_rgb(xyz, mode=mode)

    def load_lookup_table(filename):
        df = pd.read_csv(filename)
        return df['Color Temperature (K)'].values, df['Brightness'].values

    def save_rgb_to_csv(cct_values,brightness_values, output_filename, mode='none'):
        rgb_values = []

        for cct,brightness in zip(cct_values, brightness_values):
            converter = ColorTemperatureConverter(cct, warmness=0.9)
            #print('in save functino mode is', mode)
            rgb = converter.get_rgb(mode=mode)
            rgb_values.append((cct, *rgb, brightness))

        # Create a DataFrame and save to CSV
        rgb_df = pd.DataFrame(rgb_values, columns=['CCT (K)', 'R', 'G', 'B', 'Brightness'])
        rgb_df.to_csv(output_filename, index=False)
        print(f"RGB values saved to {output_filename}")
    # Load the color temperature values from the CSV
    cct_values, brightness_values = load_lookup_table('generated_circadian_cct_brightness.csv')
    
    # Save the RGB values to a new CSV
    save_rgb_to_csv(cct_values,brightness_values, 'rgb_values.csv', mode)
# Global variables
csv_file = 'rgb_values.csv'
last_manual_input_time = None
testing_mode = False
stop_threads = Event()
ESP32_URL = "http://esp-light.local/set_color"

# Load CSV data
try:
    data = pd.read_csv(csv_file)
except FileNotFoundError:
    data = pd.DataFrame(columns=['R', 'G', 'B', 'Brightness'])

def get_sunrise_sunset_times(lat, lng, date=None, tzid=None):
    """Get sunrise and sunset times from the API"""
    params = {
        'lat': lat,
        'lng': lng,
        'formatted': 0
    }
    if date:
        params['date'] = date
    if tzid:
        params['tzid'] = tzid

    try:
        response = requests.get('https://api.sunrise-sunset.org/json', params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            return data['results']['sunrise'], data['results']['sunset']
        else:
            return None, None
    except Exception as e:
        print(f"Error fetching sunrise-sunset data: {e}")
        return None, None

def send_to_esp32(r, g, b, brightness):
    """Send color data to ESP32"""
    payload = {'R': r, 'G': g, 'B': b, 'Brightness': brightness}
    try:
        response = requests.post(ESP32_URL, data=payload)
        if response.status_code == 200:
            print("Command sent to ESP32 successfully.")
        else:
            print("Failed to send command to ESP32.")
    except Exception as e:
        print(f"Error: {e}")

def get_current_values():
    """Get current color values based on time"""
    current_time = datetime.now().strftime('%H:%M')
    row = data.iloc[int(datetime.now().strftime('%H')) * 12 + int(datetime.now().strftime('%M')) // 5]
    return int(row['R']), int(row['G']), int(row['B']), (float(row['Brightness']) + 0.2)

def sync_with_csv():
    """Background task to sync ESP32 with CSV file"""
    global last_manual_input_time, testing_mode, stop_threads
    last_values = None
    while not stop_threads.is_set():
        if not testing_mode:
            current_time = datetime.now()
            
            if last_manual_input_time is None or (current_time - last_manual_input_time) > timedelta(seconds=20):
                current_values = get_current_values()
                if last_values != current_values:
                    send_to_esp32(*current_values)
                    last_values = current_values
        time.sleep(20)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_location_data', methods=['POST'])
def get_location_data():
    data = request.json
    lat = data.get('latitude')
    lng = data.get('longitude')
    tzid = data.get('timezone')

    sunrise, sunset = get_sunrise_sunset_times(lat, lng, tzid=tzid)
    
    if sunrise and sunset:
        tz = pytz.timezone(tzid)
        sunrise_dt = datetime.fromisoformat(sunrise).astimezone(tz)
        sunset_dt = datetime.fromisoformat(sunset).astimezone(tz)
        
        sunrise_time = sunrise_dt.strftime("%I:%M %p")
        sunset_time = sunset_dt.strftime("%I:%M %p")
        
        # Generate lighting schedule based on sunrise/sunset
        generate_lighting_schedule(sunrise_time, sunset_time)
        
        return jsonify({
            'status': 'success',
            'sunrise': sunrise_time,
            'sunset': sunset_time,
            'timezone': tzid
        })
    
    return jsonify({'status': 'error', 'message': 'Failed to get sunrise/sunset times'})

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

@app.route('/test_csv')
def test_csv():
    global testing_mode, stop_threads
    testing_mode = True
    stop_threads.clear()

    def run_test():
        for index, row in data.iterrows():
            if stop_threads.is_set():
                return
            r, g, b, brightness = int(row['R']), int(row['G']), int(row['B']), min(1, float(row['Brightness']+0.2))
            send_to_esp32(r, g, b, brightness)
            print(f"Testing row {index}: R={r}, G={g}, B={b}, Brightness={brightness}")
            time.sleep(0.001)
        
        global testing_mode
        testing_mode = False
        print("Test completed. Returning to normal operation.")
        global last_manual_input_time
        last_manual_input_time = None

    Thread(target=run_test).start()
    return "Testing CSV values. Please wait..."

@app.route('/return_to_normal')
def return_to_normal():
    global testing_mode, stop_threads
    testing_mode = False
    stop_threads.set()
    time.sleep(1)
    
    stop_threads.clear()
    Thread(target=sync_with_csv, daemon=True).start()
    
    return "Returning to normal operation.", 200

@app.route('/restart_server')
def restart_server():
    def restart():
        print("Server restarting...")
        os.execv(sys.executable, ['python'] + [" ", sys.argv[0]])
    
    Thread(target=restart).start()
    return "Server restarting...", 200

def generate_lighting_schedule(sunrise_time, sunset_time, mode='none'):
    """Generate lighting schedule based on sunrise and sunset times"""
    # Call your existing step1 and step2 functions here
    step1(sunrise_time, sunset_time)
    step2(mode)
    global data
    data = pd.read_csv(csv_file)  # Reload the CSV after generation

@app.route('/change_mode', methods = ['POST'])
def change_mode():
    rdata = request.json
    mode = rdata.get('mode')
    try:
        step2(mode)
        global data
        data = pd.read_csv(csv_file)  # Reload the CSV after generation
        return jsonify({
            'status': 'success',
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    # Start the background CSV sync task
    Thread(target=sync_with_csv, daemon=True).start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
