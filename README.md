### How this works
## Step 1: Get the color temperature data
Use any available sources
![image](https://github.com/user-attachments/assets/e43740bd-0f46-4102-9771-11c8836842f2)
## Step 2: Convert color temperature data to RGB colors
Save the csv containing columns of time (am/pm format) and color temperature as lookup_table.csv and run `datasetGenerate.py` 
![image](https://github.com/user-attachments/assets/b1a55d05-e2a5-4625-9135-cf2e4451c82b)
The output RGB table for every 5 minutes of the day is saved as `daily_rgb_values.csv`.
![image](https://github.com/user-attachments/assets/1ab5aab0-7d9c-4bcf-9bc7-710048f8679c)

## Step 3: Use this csv lookup table in the microcontroller (arduino-only) with the RGB Lights
Avoid using Raspberry Pi as it cannot do analogWrite. We realized this after making the one-month progress report.
