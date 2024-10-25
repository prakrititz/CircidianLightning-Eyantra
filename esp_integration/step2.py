import numpy as np
import pandas as pd
import neopixel, gpiozero, board
import time
# Initialize NeoPixel
#pixels = neopixel.NeoPixel(board.D12, 6)

# Load CIE data from CSV file
cie_data = pd.read_csv('CIE_xyz_1931_2deg.csv', header=None)

# Extract wavelength and color matching functions data
wavelengths = cie_data.iloc[:, 0].values
x_bar = cie_data.iloc[:, 1].values
y_bar = cie_data.iloc[:, 2].values
z_bar = cie_data.iloc[:, 3].values

# Standard RGB transformation matrix from XYZ (sRGB color space)
xyz_to_rgb_matrix = np.array([
    [3.1341864, -1.6172090, -0.4906941],
[-0.9787485,  1.9161301,  0.0334334],
 [0.0719639, -0.2289939,  1.4057537]
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

def load_lookup_table(filename):
    df = pd.read_csv(filename)
    return df['Color Temperature (K)'].values, df['Brightness'].values

def save_rgb_to_csv(cct_values,brightness_values, output_filename):
    rgb_values = []

    for cct,brightness in zip(cct_values, brightness_values):
        converter = ColorTemperatureConverter(cct)
        rgb = converter.get_rgb()
        rgb_values.append((cct, *rgb, brightness))

    # Create a DataFrame and save to CSV
    rgb_df = pd.DataFrame(rgb_values, columns=['CCT (K)', 'R', 'G', 'B', 'Brightness'])
    rgb_df.to_csv(output_filename, index=False)
    print(f"RGB values saved to {output_filename}")

if __name__ == "__main__":
    # Load the color temperature values from the CSV
    cct_values, brightness_values = load_lookup_table('generated_circadian_cct_brightness.csv')
    
    # Save the RGB values to a new CSV
    save_rgb_to_csv(cct_values,brightness_values, 'rgb_values.csv')
