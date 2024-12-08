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

experimental_data = pd.read_csv('../utils/ideal_Dataset.csv', names=["Date Time", "Standard Equipment CAS 140CT"])
experimental_data["Date Time"] = experimental_data["Date Time"].apply(convert_to_ampm)

# Load all three generated curves
gaussian_data = pd.read_csv("generated_circadian_gaussian.csv")
sinusoidal_data = pd.read_csv("generated_circadian_sinusoidal.csv")
parabolic_data = pd.read_csv("generated_circadian_parabolic.csv")
cls_model_data = pd.read_csv("generated_circadian_parabolic_fitted.csv")

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
cls_model_times = [time_to_decimal(t) for t in cls_model_data["Time"]]
experimental_hours = [time_to_decimal(t) for t in experimental_data["Date Time"]]

# Interpolation for each model
interp_gaussian = interp1d(gaussian_times, gaussian_data["Color Temperature (K)"], 
                          kind='cubic', fill_value="extrapolate")
interp_sinusoidal = interp1d(sinusoidal_times, sinusoidal_data["Color Temperature (K)"], 
                            kind='cubic', fill_value="extrapolate")
interp_parabolic = interp1d(parabolic_times, parabolic_data["Color Temperature (K)"], 
                           kind='cubic', fill_value="extrapolate")
interp_cls_model = interp1d(cls_model_times, cls_model_data["Color Temperature (K)"],kind='cubic', fill_value="extrapolate")

# Calculate generated values at experimental times
experimental_data["gaussian CCT"] = interp_gaussian(experimental_hours)
experimental_data["sinusoidal CCT"] = interp_sinusoidal(experimental_hours)
experimental_data["parabolic CCT"] = interp_parabolic(experimental_hours)
experimental_data["CLS Model CCT"] = interp_cls_model(experimental_hours)

# Calculate errors for each model
for model in ["gaussian", "sinusoidal", "parabolic", "CLS Model"]:
    experimental_data[f"{model} Error (%)"] = np.abs(
        (experimental_data[f"{model} CCT"] - experimental_data["Standard Equipment CAS 140CT"]) /
        experimental_data["Standard Equipment CAS 140CT"]
    ) * 100

# Calculate statistics for each model
stats = {}
for model in ["gaussian", "sinusoidal", "parabolic", "CLS Model"]:
    stats[model] = {
        "avg_error": experimental_data[f"{model} Error (%)"].mean(),
        "std_error": experimental_data[f"{model} Error (%)"].std(),
        "correlation": np.corrcoef(experimental_data["Standard Equipment CAS 140CT"],
                                 experimental_data[f"{model} CCT"])[0,1]
    }

# Set global font sizes
plt.rcParams.update({
    'font.size': 14,
    'axes.labelsize': 16,
    'axes.titlesize': 18,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 16  # Increased legend font size
})

# Plot comparison of all models
plt.figure(figsize=(15, 8))
# Plot other models first with reduced alpha
plt.plot(experimental_data["Date Time"],
         experimental_data["gaussian CCT"],
         label=f"Gaussian (correlation = {stats['gaussian']['correlation']:.3f})",
         color="blue",
         linestyle="--",
         alpha=0.4)
plt.plot(experimental_data["Date Time"],
         experimental_data["sinusoidal CCT"],
         label=f"Sinusoidal (correlation = {stats['sinusoidal']['correlation']:.3f})",
         color="green",
         linestyle="--",
         alpha=0.4)
plt.plot(experimental_data["Date Time"],
         experimental_data["parabolic CCT"],
         label=f"Parabolic (correlation = {stats['parabolic']['correlation']:.3f})",
         color="red",
         linestyle="--",
         alpha=0.4)
# Highlight experimental data and CLS model
plt.plot(experimental_data["Date Time"],
         experimental_data["Standard Equipment CAS 140CT"],
         label="Experimental Data",
         color="black",
         marker="o",
         linestyle=":",
         linewidth=2)
plt.plot(experimental_data["Date Time"],
         experimental_data["CLS Model CCT"],
         label=f"CLS Model (correlation = {stats['CLS Model']['correlation']:.3f})",
         color="purple",
         linestyle="-",
         linewidth=3)

plt.xlabel("Time", fontweight='bold')
plt.ylabel("Color Temperature (K)", fontweight='bold')
plt.title("Comparison of Different CCT Models with Experimental Data", pad=20)
plt.xticks(np.arange(0, len(experimental_data["Date Time"]), 10), 
           experimental_data["Date Time"][::10],
           rotation=45)
plt.margins(x=0.02)
plt.legend(frameon=True, 
          fancybox=True, 
          shadow=True,
          framealpha=1,  # Solid background
          edgecolor='black',  # Black edge for better visibility
          borderpad=1,  # More padding inside legend
          labelspacing=1.2)  # More space between legend entriesplt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("model_comparison.png", dpi=300, bbox_inches='tight')
plt.show()

# Plot error distributions with enhanced visibility
plt.figure(figsize=(15, 6))
width = 0.25
x = np.arange(len(experimental_data["Date Time"]))
plt.bar(x, experimental_data["gaussian Error (%)"], width, label="Gaussian", color="blue", alpha=0.4)
plt.bar(x, experimental_data["sinusoidal Error (%)"], width, label="Sinusoidal", color="green", alpha=0.4)
plt.bar(x, experimental_data["parabolic Error (%)"], width, label="Parabolic", color="red", alpha=0.4)
plt.bar(x, experimental_data["CLS Model Error (%)"], width, label="CLS Model", color="purple", alpha=0.8)
plt.xlabel("Time", fontweight='bold')
plt.ylabel("Error (%)", fontweight='bold')
plt.title("Error Distribution Comparison", pad=20)
plt.xticks(x[::10], experimental_data["Date Time"][::10], rotation=45)
plt.margins(x=0.02)
plt.legend(frameon=True, fancybox=True, shadow=True)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("error_comparison.png", dpi=300, bbox_inches='tight')
plt.show()

# Plot correlation comparison with enhanced visibility
plt.figure(figsize=(10, 6))
models = ["Gaussian", "Sinusoidal", "Parabolic", "CLS Model"]
correlations = [stats[model]["correlation"] for model in ["gaussian", "sinusoidal", "parabolic", "CLS Model"]]
colors = ['blue', 'green', 'red', 'purple']
bars = plt.bar(models, correlations, color=colors)
bars[-1].set_alpha(1.0)  # Highlight CLS Model
for bar in bars[:-1]:
    bar.set_alpha(0.4)
plt.ylabel("Correlation Coefficient", fontweight='bold')
plt.title("Model Correlations with Experimental Data", pad=20)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("correlation_comparison.png", dpi=300, bbox_inches='tight')
plt.show()

# Save detailed results
experimental_data.to_csv("model_comparison_results.csv", index=False)
