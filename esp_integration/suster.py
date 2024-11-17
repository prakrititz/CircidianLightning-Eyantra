import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from datetime import datetime

# Load experimental data with proper time format
experimental_data = pd.DataFrame({
    "Date Time": ["07:12 AM", "07:13 AM", "07:14 AM", "07:15 AM", 
                  "09:30 AM", "09:31 AM", "09:32 AM", "09:33 AM",
                  "12:00 PM", "12:01 PM", "12:02 PM", "12:03 PM",
                  "02:30 PM", "02:31 PM", "02:32 PM", "02:33 PM", 
                  "03:00 PM", "03:01 PM", "03:02 PM", "03:03 PM",
                  "06:08 PM", "06:09 PM", "06:09 PM", "06:10 PM"],
    "Standard Equipment CAS 140CT": [4681.87, 4588.73, 4518.28, 4490.18, 
                                   5388.59, 5397.74, 5410.07, 5415.24,
                                   5459.03, 5464.97, 5470.72, 5471.18, 
                                   5628.06, 5627.67, 5626.42, 5623.91,
                                   5427.2, 5467.1, 5506.61, 5526.2,
                                   4171.02, 4150.36, 4122.84, 4102.23],
})

# Load generated CCT data
generated_data = pd.read_csv("generated_circadian_cct_brightness.csv")

def convert_to_24hr(time_str):
    return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")

def time_to_decimal(time_str):
    time_24 = convert_to_24hr(time_str)
    hours = int(time_24.split(":")[0])
    minutes = int(time_24.split(":")[1])
    return hours + minutes/60

# Convert times for calculations
generated_times = [time_to_decimal(t) for t in generated_data["Time"]]
experimental_hours = [time_to_decimal(t) for t in experimental_data["Date Time"]]

# Interpolation
interp_cct = interp1d(generated_times, 
                      generated_data["Color Temperature (K)"], 
                      kind='cubic', 
                      fill_value="extrapolate")

generated_cct_at_experiment_times = interp_cct(experimental_hours)

# Calculate error
experimental_data["Generated CCT"] = generated_cct_at_experiment_times
experimental_data["Error (%)"] = np.abs(
    (experimental_data["Generated CCT"] - experimental_data["Standard Equipment CAS 140CT"]) /
    experimental_data["Standard Equipment CAS 140CT"]
) * 100

# Calculate statistics
avg_error = experimental_data["Error (%)"].mean()
std_error = experimental_data["Error (%)"].std()
correlation = np.corrcoef(experimental_data["Standard Equipment CAS 140CT"], 
                         experimental_data["Generated CCT"])[0,1]

# Plot comparison
plt.figure(figsize=(12, 6))
plt.plot(experimental_data["Date Time"], 
         experimental_data["Standard Equipment CAS 140CT"], 
         label="Standard Equipment (CAS 140CT)", 
         color="blue", 
         marker="o")
plt.plot(experimental_data["Date Time"], 
         experimental_data["Generated CCT"], 
         label="Generated CCT", 
         color="orange", 
         linestyle="--", 
         marker="x")
plt.xlabel("Time")
plt.ylabel("Color Temperature (K)")
plt.title(f"Comparison of Generated and Experimental CCT Values\n" 
          f"Avg Error: {avg_error:.2f}%, Std Dev: {std_error:.2f}%\n"
          f"Correlation: {correlation:.4f}")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("comparison_generated_vs_experimental.png")
plt.show()

# Plot error distribution
plt.figure(figsize=(12, 6))
plt.bar(experimental_data["Date Time"], 
        experimental_data["Error (%)"], 
        color="red", 
        alpha=0.7, 
        label="Error (%)")
plt.xlabel("Time")
plt.ylabel("Error (%)")
plt.title("Error Distribution in Generated CCT vs Experimental Data")
plt.xticks(rotation=45)
plt.grid(axis="y")
plt.legend()
plt.tight_layout()
plt.savefig("error_analysis.png")
plt.show()

# Save results
experimental_data.to_csv("comparison_with_errors.csv", index=False)
