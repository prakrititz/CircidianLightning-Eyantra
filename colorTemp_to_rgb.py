import numpy as np
import pandas as pd

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

    def visualize_rgb_terminal(self):
        """Visualize the RGB color in the terminal using ANSI escape codes."""
        rgb = self.get_rgb()
        r, g, b = rgb
        print(f"\033[48;2;{r};{g};{b}m   \033[0m CCT: {self.cct}K -> RGB: {rgb}")

# Example usage:
if __name__ == "__main__":
    cct = 6500  # Example color temperature
    converter = ColorTemperatureConverter(cct)
    converter.visualize_rgb_terminal()
