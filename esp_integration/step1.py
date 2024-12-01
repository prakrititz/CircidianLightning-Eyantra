import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
MAX_COLOR_TEMP = 5700
MIN_COLOR_TEMP = 4000
AMPLITUDE = MAX_COLOR_TEMP-MIN_COLOR_TEMP
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
    cct_fit = np.where((t_smooth < sunrise_hour) | (t_smooth > sunset_hour), MIN_COLOR_TEMP, cct_fit)
    cct_fit = np.clip(cct_fit, MIN_COLOR_TEMP, MAX_COLOR_TEMP)

    # Calculate brightness (normalized between 0 and 1)
    brightness = (cct_fit - MIN_COLOR_TEMP) / (MAX_COLOR_TEMP - MIN_COLOR_TEMP)
    brightness = np.clip(brightness, 0, 1)

    return t_smooth, cct_fit, brightness

def generate_cct_curve_sinusoidal(sunrise, sunset, reference_data):
    sunrise_hour = time_to_hours(sunrise)
    sunset_hour = time_to_hours(sunset)
    
    # Calculate midday point and scale factor
    midday = sunrise_hour + (sunset_hour - sunrise_hour) / 2
    daylight_duration = sunset_hour - sunrise_hour
    scale_factor = 12 / daylight_duration  # Normalize to 12-hour period
    
    t_smooth = np.arange(0, 24, 5/60)
    transition_period = 0.5  # 30 minutes transition
    
    def sinusoidal(t):
        # Scale time around midday
        scaled_t = (t - midday) * scale_factor
        # Sine wave scaled to CCT range (MIN_COLOR_TEMPK to MAX_COLOR_TEMPK)
        return MIN_COLOR_TEMP + AMPLITUDE * (1 + np.cos(np.pi * scaled_t / 6)) / 2
    
    cct_fit = sinusoidal(t_smooth)
    
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

def generate_cct_curve_parabolic_fitted(sunrise, sunset, reference_data):
    sunrise_hour = time_to_hours(sunrise)
    sunset_hour = time_to_hours(sunset)
    
    # Calculate the midday point
    midday = sunrise_hour + (sunset_hour - sunrise_hour) / 2
    daylight_duration = sunset_hour - sunrise_hour
    
    t_smooth = np.arange(0, 24, 5/60)  # Generate time points in 5-minute intervals
    transition_period = 0.5  # 30-minute transition for smoothing
    
    def parabolic(t):
        # Calculate parabola coefficient dynamically for the given day length
        a = -AMPLITUDE / ((daylight_duration / 2) ** 2)
        return MIN_COLOR_TEMP + a * (t - midday) ** 2 + AMPLITUDE
    
    cct_fit = parabolic(t_smooth)
    
    # Apply smoothing for transitions
    sunrise_mask = (t_smooth >= (sunrise_hour - transition_period)) & (t_smooth <= sunrise_hour)
    sunset_mask = (t_smooth >= sunset_hour) & (t_smooth <= (sunset_hour + transition_period))
    
    # Smooth ramp-up and ramp-down
    sunrise_factor = (t_smooth[sunrise_mask] - (sunrise_hour - transition_period)) / transition_period
    sunset_factor = 1 - (t_smooth[sunset_mask] - sunset_hour) / transition_period
    
    cct_fit[sunrise_mask] = MIN_COLOR_TEMP + (cct_fit[sunrise_mask] - MIN_COLOR_TEMP) * sunrise_factor
    cct_fit[sunset_mask] = MIN_COLOR_TEMP + (cct_fit[sunset_mask] - MIN_COLOR_TEMP) * sunset_factor
    
    # Set values outside the sunrise-sunset range to the minimum CCT
    cct_fit[t_smooth < (sunrise_hour - transition_period)] = MIN_COLOR_TEMP
    cct_fit[t_smooth > (sunset_hour + transition_period)] = MIN_COLOR_TEMP
    
    # Clip CCT values to the allowable range
    cct_fit = np.clip(cct_fit, MIN_COLOR_TEMP, MAX_COLOR_TEMP)
    
    # Calculate brightness as a normalized value between 0 and 1
    brightness = (cct_fit - MIN_COLOR_TEMP) / AMPLITUDE
    brightness = np.clip(brightness, 0, 1)
    
    return t_smooth, cct_fit, brightness

def convert_to_ampm(decimal_time):
    hours = int(decimal_time / 60)
    minutes = int(decimal_time % 60)
    period = "AM" if hours < 12 else "PM"
    hours = hours if hours <= 12 else hours - 12
    hours = 12 if hours == 0 else hours
    return f"{hours:02d}:{minutes:02d} {period}"

# Generate all three curve types
sunrise_time = input("Enter sunrise time (e.g., 7:00AM): ")
sunset_time = input("Enter sunset time (e.g., 7:00PM): ")
reference_data = './input_data.csv'

# Generate curves
t_gauss, cct_gauss, bright_gauss = generate_cct_curve(sunrise_time, sunset_time, reference_data)
t_sin, cct_sin, bright_sin = generate_cct_curve_sinusoidal(sunrise_time, sunset_time, reference_data)
t_para, cct_para, bright_para = generate_cct_curve_parabolic(sunrise_time, sunset_time, reference_data)
t_para_fitted, cct_para_fitted, bright_para_fitted = generate_cct_curve_parabolic_fitted(sunrise_time, sunset_time, reference_data)

# Save each curve to separate CSVs
for curve_type, t, cct, brightness in [
    ('gaussian', t_gauss, cct_gauss, bright_gauss),
    ('sinusoidal', t_sin, cct_sin, bright_sin),
    ('parabolic', t_para, cct_para, bright_para),
    ('parabolic_fitted', t_para_fitted, cct_para_fitted, bright_para_fitted)
]:
    df = pd.DataFrame({
        'Time': [hours_to_time_str(h) for h in t],
        'Color Temperature (K)': np.round(cct).astype(int),
        'Brightness': np.round(brightness, 2)
    })
    df.to_csv(f'generated_circadian_{curve_type}.csv', index=False)

    # Plot individual curves
    plt.figure(figsize=(12, 6))
    plt.plot(t, cct, label='Color Temperature (K)', color='blue')
    plt.plot(t, brightness * (MAX_COLOR_TEMP), label='Brightness', color='yellow', linestyle='--')
    plt.xlabel('Time (hours)')
    plt.ylabel('Value')
    plt.title(f'{curve_type.capitalize()} Circadian Rhythm\nSunrise: {sunrise_time}, Sunset: {sunset_time}')
    plt.xticks(range(0, 25, 2))
    plt.xlim(time_to_hours(sunrise_time), time_to_hours(sunset_time))
    plt.ylim(0, 8000)
    plt.legend()
    plt.grid(True)
    plt.savefig(f'generated_circadian_{curve_type}.png')
    plt.close()
