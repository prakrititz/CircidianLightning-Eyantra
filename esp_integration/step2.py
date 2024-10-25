import numpy as np
import pandas as pd
import neopixel, gpiozero, board
import time
# Initialize NeoPixelpixels = neopixel.NeoPixel(board.D12, 6)

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

if __name__ == "__main__":
    # Load the color temperature values from the CSV
    cct_values, brightness_values = load_lookup_table('generated_circadian_cct_brightness.csv')
    
    # Save the RGB values to a new CSV
    save_rgb_to_csv(cct_values,brightness_values, 'rgb_values.csv')
