import pandas as pd
#import neopixel
i#mport gpiozero
import board
import time

# Initialize NeoPixel
#pixels = neopixel.NeoPixel(board.D12, 12)
#pixels.fill((0, 0, 0))


def load_rgb_from_csv(filename):
    df = pd.read_csv(filename)
    return df[['R', 'G', 'B']].values
 
def load_brightness_from_csv(filename):
	df = pd.read_csv(filename)
	return df['Brightness'].values

if __name__ == "__main__":
    try:
        pixels.fill((0, 0, 0))
        # Load the RGB values from the CSV
        rgb_values = load_rgb_from_csv('rgb_values.csv')
        brightness_values = load_brightness_from_csv('rgb_values.csv')
        # Display the colors on NeoPixel
        for rgb,brightness in zip(rgb_values, brightness_values):
            r, g, b = rgb
            pixels[5] = ((r, g, b))
            pixels[6] = ((r, g, b))
            pixels[7] = ((r, g, b))
            pixels.brightness = min(1, brightness+0.03)
            print(f"Displaying RGB: ({r}, {g}, {b})")
            time.sleep(0.2)

    except KeyboardInterrupt:
        pass
    finally:
        pixels.fill((0, 0, 0))  # Turn off the pixels
