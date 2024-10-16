<h1 align="center">🌈 RGB Simulator for Circadian Lighting 🌙</h1>

<p align="center">
  <img src="https://github.com/user-attachments/assets/e43740bd-0f46-4102-9771-11c8836842f2" alt="Color Temperature Data" width="600">
</p>

<h2>🚀 How this works</h2>

<h3>📊 Step 1: Get the color temperature data</h3>

<p>Use any available sources to obtain color temperature data throughout the day.</p>

<h3>🔢 Step 2: Convert color temperature data to RGB colors</h3>

<p>Save the CSV containing columns of time (AM/PM format) and color temperature as <code>lookup_table.csv</code> and run <code>datasetGenerate.py</code>.</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/b1a55d05-e2a5-4625-9135-cf2e4451c82b" alt="Dataset Generation" width="600">
</p>

<p>The output RGB table for every 5 minutes of the day is saved as <code>daily_rgb_values.csv</code>.</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/08e4831f-4263-4e2f-81c1-3314235bf466" alt="RGB Values CSV" width="600">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/e64d1fb9-1936-4719-86f6-d2d588070336" alt="RGB Values Graph" width="600">
</p>

<h3>💡 Step 3: Use this CSV lookup table in the microcontroller (Arduino-only) with the RGB Lights</h3>

<p><strong>Note:</strong> ⚠️ Avoid using Raspberry Pi as it cannot do analogWrite. We realized this after making the one-month progress report.</p>

<p>Alternatively, you can see the matplotlib simulation in <code>rgb_simulator_matplotlib.py</code>, which quickly runs through the course of the day showing the Circadian Lighting we desire on your monitor's screen.</p>

<p align="center">
  https://github.com/user-attachments/assets/fc1340b0-df47-4129-b7dd-34b321cdb9d1
</p>

<style>
  body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }
  h1, h2, h3 {
    color: #2c3e50;
  }
  code {
    background-color: #f4f4f4;
    padding: 2px 4px;
    border-radius: 4px;
  }
  img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  }
</style>
