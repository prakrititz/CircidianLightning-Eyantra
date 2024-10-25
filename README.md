<h1 align="center">🌈 RGB Simulator for Circadian Lighting 🌙</h1>
<p align="center">
  <img src="https://github.com/user-attachments/assets/e43740bd-0f46-4102-9771-11c8836842f2" alt="Color Temperature Data" width="600">
</p>

## 🛠️ Installation
Before starting, install the required Python packages:
```bash
pip install -r requirements.txt
```

## 🌟 Technical Overview
This project implements circadian lighting using a sophisticated color temperature conversion process:

1. **Color Temperature Distribution**
   - We model the daily color temperature variation using a Gaussian (normal) distribution
   - The distribution is optimized to fit the given color temperature and time data
   - This ensures smooth transitions throughout the day

2. **Color Temperature to RGB Conversion**
   - The conversion process follows multiple steps to ensure accuracy:
     1. Use Planck's laws to convert color temperatures to wavelengths
     2. Filter through L, M, and S cone responses
     3. Convert to CIE 1931 color space using color matching functions
     4. Transform CIE 1931 values to RGB using a conversion matrix

3. **Color Correction**
   - Due to known limitations in the CIE 1931 color space (which tends to produce bluish values)
   - We implement a "warmness" correction using a custom matrix in `step2.py`
   - This correction helps achieve more natural and comfortable lighting

**Note:** While this implementation provides a close approximation of natural color temperatures, small margins of error may exist due to inherent limitations in color space conversions.

## 🚀 How this works

### 📊 Step 1: Get the color temperature data (Optional)
Use any available sources to obtain color temperature data throughout the day. This step can be skipped as default values are provided.

### 💡 Step 2: Hardware Implementation with ESP32 + NeoPixel

#### Hardware Requirements
- ESP32 development board
- NeoPixel LED ring
- Common WiFi network
- Computer to run the Python server

**Important:** Both the ESP32 and the computer running the Python server must be connected to the same WiFi network.

#### Hardware Connections
1. Power the ESP32
2. Connect 5V and GND to NeoPixel
3. Connect NeoPixel ground to ESP32 ground (ensures common ground level)
4. Connect ESP32's GPIO 13 to NeoPixel's DI pin

#### Software Setup
1. In `esp_integration` folder, modify the ESP32 code:
   - Enter your WiFi SSID and password
   - Upload to ESP32
   - Note down the ESP32's IP address

2. On the Python server:
   - Update `clientCode_step3.py` with ESP32's IP address
   - Run the following files in order:
     1. `step1.py` (You'll be prompted for sunrise/sunset times)
     2. `step2.py`
     3. `clientCode_step3.py`

#### Features
- Flask web interface for:
  - Manual RGB value control
  - Circadian rhythm simulation control
  - Return to automatic mode
- Automatic circadian rhythm when left unattended

#### Other Implementation Options
Arduino and Simulation modes are planned for future releases.

## 🔜 Next Steps
* Integration with sunset/sunrise by location API to automatically configure circadian lighting for any location/timezone

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
