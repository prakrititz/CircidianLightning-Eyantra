import numpy as np
import pandas as pd
import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta

# Setup GPIO pins for the RGB LED
RED_PIN = 12
GREEN_PIN = 13
BLUE_PIN = 19
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(BLUE_PIN, GPIO.OUT)

# Set up PWM for each LED color
red_pwm = GPIO.PWM(RED_PIN, 100)   # 100 Hz PWM frequency
green_pwm = GPIO.PWM(GREEN_PIN, 100)
blue_pwm = GPIO.PWM(BLUE_PIN, 100)

# Start PWM with 0% duty cycle (off)
red_pwm.start(0)
green_pwm.start(0)
blue_pwm.start(0)

# Load CIE data from CSV file
cie_data = pd.read_csv('CIE_xyz_1931_2deg.csv', header=None)

# Extract wavelength and color matching functions data
wavelengths = cie_data.iloc[:, 0].values
x_bar = cie_data.iloc[:, 1].values
y_bar = cie_data.iloc[:, 2].values
z_bar = cie_data.iloc[:, 3].values

# Standard RGB transformation matrix from XYZ (sRGB color space)
xyz_to_rgb_matrix = np.array([
    [3.2406, -1.5372, -0.4986],
    [-0.9689, 1.8758, 0.0415],
    [0.0557, -0.2040, 1.0570]
])

class ColorTemperatureConverter:
    def __init__(self, cct):
        self.cct = cct

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
        rgb = np.dot(xyz_to_rgb_matrix, xyz)
        rgb = np.clip(rgb, 0, 1)
        rgb = (rgb * 255).astype(int)
        return rgb

    def get_rgb(self):
        xyz = self.cct_to_xyz()
        return self.xyz_to_rgb(xyz)

    def visualize_rgb_led(self):
        rgb = self.get_rgb()
        r, g, b = rgb
        red_pwm.ChangeDutyCycle(r * 100 / 255)
        green_pwm.ChangeDutyCycle(g * 100 / 255)
        blue_pwm.ChangeDutyCycle(b * 100 / 255)
        print(f"CCT: {self.cct}K -> RGB: {rgb}")

def load_lookup_table(filename):
    df = pd.read_csv(filename)
    df['Time'] = pd.to_datetime(df['Time'], format='%I:%M %p').dt.time
    return df

def interpolate_color_temperature(lookup_table, current_time):
    current_time = current_time.time()
    
    # Find the two closest times in the lookup table
    lower_time = lookup_table[lookup_table['Time'] <= current_time]['Time'].max()
    upper_time = lookup_table[lookup_table['Time'] > current_time]['Time'].min()
    
    if pd.isnull(lower_time):
        lower_time = lookup_table['Time'].max()
    if pd.isnull(upper_time):
        upper_time = lookup_table['Time'].min()
    
    lower_temp = lookup_table[lookup_table['Time'] == lower_time]['Color Temperature (K)'].values[0]
    upper_temp = lookup_table[lookup_table['Time'] == upper_time]['Color Temperature (K)'].values[0]
    
    # Convert times to total seconds for interpolation
    current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
    lower_seconds = lower_time.hour * 3600 + lower_time.minute * 60 + lower_time.second
    upper_seconds = upper_time.hour * 3600 + upper_time.minute * 60 + upper_time.second
    
    # Handle midnight crossing
    if upper_seconds < lower_seconds:
        upper_seconds += 24 * 3600
    if current_seconds < lower_seconds:
        current_seconds += 24 * 3600
    
    # Perform linear interpolation
    fraction = (current_seconds - lower_seconds) / (upper_seconds - lower_seconds)
    interpolated_temp = lower_temp + fraction * (upper_temp - lower_temp)
    
    return int(round(interpolated_temp))

if __name__ == "__main__":
    try:
        lookup_table = load_lookup_table('lookup_table.csv')
        
        while True:
            current_time = datetime.now()
            cct = interpolate_color_temperature(lookup_table, current_time)
            converter = ColorTemperatureConverter(cct)
            converter.visualize_rgb_led()
            
            # Wait until the next 5-minute mark
            next_update = current_time + timedelta(minutes=5)
            next_update = next_update.replace(minute=next_update.minute // 5 * 5, second=0, microsecond=0)
            time.sleep((next_update - current_time).total_seconds())
    
    except KeyboardInterrupt:
        pass
    finally:
        red_pwm.stop()
        green_pwm.stop()
        blue_pwm.stop()
        GPIO.cleanup()
