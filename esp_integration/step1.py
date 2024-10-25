import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

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

# Example usage
sunrise_time = input("Enter sunrise time (e.g., 7:00AM): ")
sunset_time = input("Enter sunset time (e.g., 7:00PM): ")
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
