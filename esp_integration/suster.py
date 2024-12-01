import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from datetime import datetime

def convert_to_ampm(decimal_time):
    hours = int(decimal_time / 60)
    minutes = int(decimal_time % 60)
    period = "AM" if hours < 12 else "PM"
    hours = hours if hours <= 12 else hours - 12
    hours = 12 if hours == 0 else hours
    return f"{hours:02d}:{minutes:02d} {period}"

experimental_data = pd.read_csv('../ideal_Dataset.csv', names=["Date Time", "Standard Equipment CAS 140CT"])
experimental_data["Date Time"] = experimental_data["Date Time"].apply(convert_to_ampm)

# Load all three generated curves
gaussian_data = pd.read_csv("generated_circadian_gaussian.csv")
sinusoidal_data = pd.read_csv("generated_circadian_sinusoidal.csv")
parabolic_data = pd.read_csv("generated_circadian_parabolic.csv")
parabolic_fitted_data = pd.read_csv("generated_circadian_parabolic_fitted.csv")

def convert_to_24hr(time_str):
    return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")

def time_to_decimal(time_str):
    time_24 = convert_to_24hr(time_str)
    hours = int(time_24.split(":")[0])
    minutes = int(time_24.split(":")[1])
    return hours + minutes/60

# Convert times for calculations
gaussian_times = [time_to_decimal(t) for t in gaussian_data["Time"]]
sinusoidal_times = [time_to_decimal(t) for t in sinusoidal_data["Time"]]
parabolic_times = [time_to_decimal(t) for t in parabolic_data["Time"]]
parabolic_fitted_times = [time_to_decimal(t) for t in parabolic_fitted_data["Time"]]
experimental_hours = [time_to_decimal(t) for t in experimental_data["Date Time"]]

# Interpolation for each model
interp_gaussian = interp1d(gaussian_times, gaussian_data["Color Temperature (K)"], 
                          kind='cubic', fill_value="extrapolate")
interp_sinusoidal = interp1d(sinusoidal_times, sinusoidal_data["Color Temperature (K)"], 
                            kind='cubic', fill_value="extrapolate")
interp_parabolic = interp1d(parabolic_times, parabolic_data["Color Temperature (K)"], 
                           kind='cubic', fill_value="extrapolate")
interp_parabolic_fitted = interp1d(parabolic_fitted_times, parabolic_fitted_data["Color Temperature (K)"],kind='cubic', fill_value="extrapolate")

# Calculate generated values at experimental times
experimental_data["Gaussian CCT"] = interp_gaussian(experimental_hours)
experimental_data["Sinusoidal CCT"] = interp_sinusoidal(experimental_hours)
experimental_data["Parabolic CCT"] = interp_parabolic(experimental_hours)
experimental_data["Parabolic Fitted CCT"] = interp_parabolic_fitted(experimental_hours)

# Calculate errors for each model
for model in ["Gaussian", "Sinusoidal", "Parabolic", "Parabolic Fitted"]:
    experimental_data[f"{model} Error (%)"] = np.abs(
        (experimental_data[f"{model} CCT"] - experimental_data["Standard Equipment CAS 140CT"]) /
        experimental_data["Standard Equipment CAS 140CT"]
    ) * 100

# Calculate statistics for each model
stats = {}
for model in ["Gaussian", "Sinusoidal", "Parabolic", "Parabolic Fitted"]:
    stats[model] = {
        "avg_error": experimental_data[f"{model} Error (%)"].mean(),
        "std_error": experimental_data[f"{model} Error (%)"].std(),
        "correlation": np.corrcoef(experimental_data["Standard Equipment CAS 140CT"],
                                 experimental_data[f"{model} CCT"])[0,1]
    }

# Plot comparison of all models
plt.figure(figsize=(15, 8))
plt.plot(experimental_data["Date Time"],
         experimental_data["Standard Equipment CAS 140CT"],
         label="Experimental Data",
         color="black",
         marker="o",
         linestyle=":")
plt.plot(experimental_data["Date Time"],
         experimental_data["Gaussian CCT"],
         label="Gaussian Model",
         color="blue",
         linestyle="--")
plt.plot(experimental_data["Date Time"],
         experimental_data["Sinusoidal CCT"],
         label="Sinusoidal Model",
         color="green",
         linestyle="--")
plt.plot(experimental_data["Date Time"],
         experimental_data["Parabolic CCT"],
         label="Parabolic Model",
         color="red",
         linestyle="--")
plt.plot(experimental_data["Date Time"],
         experimental_data["Parabolic Fitted CCT"],
         label="Parabolic Fitted Model",
         color="purple",
         linestyle="--")
plt.xlabel("Time")
plt.ylabel("Color Temperature (K)")
plt.title("Comparison of Different CCT Models with Experimental Data")
plt.xticks(np.arange(0, len(experimental_data["Date Time"]), 10), 
           experimental_data["Date Time"][::10],
           rotation=45)
plt.margins(x=0.02)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("model_comparison.png")
plt.show()

# Plot error distributions
plt.figure(figsize=(15, 6))
width = 0.25
x = np.arange(len(experimental_data["Date Time"]))
plt.bar(x, experimental_data["Gaussian Error (%)"], width, label="Gaussian", color="blue", alpha=0.7)
plt.bar(x, experimental_data["Sinusoidal Error (%)"], width, label="Sinusoidal", color="green", alpha=0.7)
plt.bar(x, experimental_data["Parabolic Error (%)"], width, label="Parabolic", color="red", alpha=0.7)
plt.bar(x, experimental_data["Parabolic Fitted Error (%)"], width, label="Parabolic Fitted", color="purple", alpha=0.7)
plt.xlabel("Time")
plt.ylabel("Error (%)")
plt.title("Error Distribution Comparison")
plt.xticks(x[::10], experimental_data["Date Time"][::10], rotation=45)
plt.margins(x=0.02)
plt.legend()
plt.grid(axis="y")
plt.tight_layout()
plt.savefig("error_comparison.png")
plt.show()

# Plot correlation comparison
plt.figure(figsize=(10, 6))
correlations = [stats[model]["correlation"] for model in ["Gaussian", "Sinusoidal", "Parabolic", "Parabolic Fitted"]]
plt.bar(["Gaussian", "Sinusoidal", "Parabolic", "Parabolic Fitted"], correlations)
plt.ylabel("Correlation Coefficient")
plt.title("Model Correlations with Experimental Data")
plt.grid(axis="y")
plt.tight_layout()
plt.savefig("correlation_comparison.png")
plt.show()

# Save detailed results
experimental_data.to_csv("model_comparison_results.csv", index=False)
