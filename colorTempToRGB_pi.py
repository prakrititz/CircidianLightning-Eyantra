import numpy as np
import pandas as pd
import RPi.GPIO as GPIO
import time

# Setup GPIO pins for the RGB LED
RED_PIN = 17
GREEN_PIN = 27
BLUE_PIN = 22

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
        """Initialize with the desired color temperature in Kelvin."""
        self.cct = cct

    def planck_law(self, wavelength):
        """Calculate spectral radiance using Planck's Law."""
        h = 6.62607015e-34  # Planck constant
        c = 2.99792458e8    # Speed of light
        k = 1.380649e-23    # Boltzmann constant
        l = wavelength * 1e-9  # Convert to meters
        return (2 * h * c ** 2) / (l ** 5) * (1 / (np.exp(h * c / (l * k * self.cct)) - 1))

    def cct_to_xyz(self):
        """Convert the stored CCT (Kelvin) to XYZ using the CIE 1931 Color Matching Functions."""
        spectral_radiance = self.planck_law(wavelengths)
        X = np.trapz(spectral_radiance * x_bar, wavelengths)  # Numerical integration
        Y = np.trapz(spectral_radiance * y_bar, wavelengths)
        Z = np.trapz(spectral_radiance * z_bar, wavelengths)
        
        XYZ = np.array([X, Y, Z])
        XYZ /= np.max(XYZ)  # Normalize

        return XYZ

    def xyz_to_rgb(self, xyz):
        """Convert XYZ to RGB using the sRGB transformation matrix."""
        rgb = np.dot(xyz_to_rgb_matrix, xyz)
        rgb = np.clip(rgb, 0, 1)  # Ensure values are within [0, 1]
        rgb = (rgb * 255).astype(int)  # Convert to [0, 255] range
        return rgb

    def get_rgb(self):
        """Public method to get the RGB value for the initialized CCT."""
        xyz = self.cct_to_xyz()
        return self.xyz_to_rgb(xyz)

    def visualize_rgb_led(self):
        """Control the RGB LED based on the calculated RGB values."""
        rgb = self.get_rgb()
        r, g, b = rgb

        # Convert RGB [0-255] values to duty cycle percentages [0-100]
        red_pwm.ChangeDutyCycle(r * 100 / 255)
        green_pwm.ChangeDutyCycle(g * 100 / 255)
        blue_pwm.ChangeDutyCycle(b * 100 / 255)

        print(f"CCT: {self.cct}K -> RGB: {rgb}")

# Example usage:
if __name__ == "__main__":
    try:
        cct = 6500  # Example color temperature
        converter = ColorTemperatureConverter(cct)
        
        # Update the LED to reflect the current color temperature
        while True:
            converter.visualize_rgb_led()
            time.sleep(1)  # Update every 1 second
    except KeyboardInterrupt:
        pass
    finally:
        red_pwm.stop()
        green_pwm.stop()
        blue_pwm.stop()
        GPIO.cleanup()
