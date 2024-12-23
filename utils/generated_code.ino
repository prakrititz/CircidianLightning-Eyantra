
#include <Adafruit_NeoPixel.h>

#define PIN 12       // Pin where NeoPixel is connected
#define NUMPIXELS 12 // Number of pixels
#define BRIGHTNESS 255 // Max brightness

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

// RGB values (replace these with your actual values)
const int rgbValues[][3] = {
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 131, 45},
  {255, 134, 49},
  {255, 138, 54},
  {255, 141, 59},
  {255, 144, 64},
  {255, 147, 69},
  {255, 150, 74},
  {255, 153, 79},
  {255, 156, 85},
  {255, 158, 90},
  {255, 161, 95},
  {255, 163, 101},
  {255, 165, 106},
  {255, 167, 111},
  {255, 169, 116},
  {255, 171, 122},
  {255, 173, 127},
  {255, 174, 132},
  {255, 176, 137},
  {255, 177, 142},
  {255, 179, 147},
  {255, 180, 152},
  {255, 181, 156},
  {255, 182, 160},
  {255, 182, 165},
  {255, 183, 169},
  {255, 184, 173},
  {255, 184, 177},
  {255, 185, 180},
  {255, 185, 184},
  {255, 186, 188},
  {255, 186, 191},
  {255, 187, 195},
  {255, 187, 198},
  {255, 188, 201},
  {255, 188, 204},
  {255, 188, 207},
  {255, 189, 210},
  {255, 189, 213},
  {255, 189, 216},
  {255, 189, 218},
  {255, 190, 221},
  {255, 190, 223},
  {255, 190, 225},
  {255, 190, 227},
  {255, 190, 229},
  {255, 190, 231},
  {255, 189, 231},
  {255, 188, 231},
  {255, 187, 232},
  {255, 186, 232},
  {255, 186, 232},
  {255, 185, 232},
  {255, 184, 232},
  {255, 184, 232},
  {255, 183, 232},
  {255, 183, 233},
  {255, 182, 233},
  {255, 182, 233},
  {255, 182, 233},
  {255, 181, 233},
  {255, 181, 233},
  {255, 181, 233},
  {255, 181, 233},
  {255, 181, 233},
  {255, 181, 233},
  {255, 181, 233},
  {255, 182, 233},
  {255, 182, 233},
  {255, 182, 233},
  {255, 183, 233},
  {255, 183, 232},
  {255, 184, 232},
  {255, 184, 232},
  {255, 185, 232},
  {255, 186, 232},
  {255, 187, 232},
  {255, 187, 232},
  {255, 188, 231},
  {255, 189, 231},
  {255, 191, 231},
  {255, 190, 229},
  {255, 190, 227},
  {255, 190, 225},
  {255, 190, 222},
  {255, 190, 220},
  {255, 189, 218},
  {255, 189, 215},
  {255, 189, 212},
  {255, 188, 210},
  {255, 188, 207},
  {255, 188, 204},
  {255, 187, 201},
  {255, 187, 197},
  {255, 187, 194},
  {255, 186, 191},
  {255, 186, 187},
  {255, 185, 183},
  {255, 185, 180},
  {255, 184, 176},
  {255, 184, 172},
  {255, 183, 168},
  {255, 182, 164},
  {255, 182, 160},
  {255, 181, 155},
  {255, 180, 151},
  {255, 179, 146},
  {255, 177, 141},
  {255, 176, 136},
  {255, 174, 131},
  {255, 172, 126},
  {255, 171, 121},
  {255, 169, 115},
  {255, 167, 110},
  {255, 165, 105},
  {255, 163, 100},
  {255, 160, 94},
  {255, 158, 89},
  {255, 155, 84},
  {255, 152, 78},
  {255, 150, 73},
  {255, 147, 68},
  {255, 144, 63},
  {255, 140, 58},
  {255, 137, 53},
  {255, 133, 48},
  {255, 130, 44},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
  {255, 129, 43},
};

const float brightnessValues[] = {
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.01,  // Brightness
  0.02,  // Brightness
  0.04,  // Brightness
  0.06,  // Brightness
  0.08,  // Brightness
  0.1,  // Brightness
  0.12,  // Brightness
  0.14,  // Brightness
  0.16,  // Brightness
  0.18,  // Brightness
  0.2,  // Brightness
  0.22,  // Brightness
  0.24,  // Brightness
  0.25,  // Brightness
  0.27,  // Brightness
  0.29,  // Brightness
  0.31,  // Brightness
  0.33,  // Brightness
  0.35,  // Brightness
  0.37,  // Brightness
  0.39,  // Brightness
  0.41,  // Brightness
  0.43,  // Brightness
  0.45,  // Brightness
  0.47,  // Brightness
  0.49,  // Brightness
  0.5,  // Brightness
  0.52,  // Brightness
  0.54,  // Brightness
  0.56,  // Brightness
  0.58,  // Brightness
  0.59,  // Brightness
  0.61,  // Brightness
  0.63,  // Brightness
  0.64,  // Brightness
  0.66,  // Brightness
  0.67,  // Brightness
  0.69,  // Brightness
  0.7,  // Brightness
  0.72,  // Brightness
  0.73,  // Brightness
  0.74,  // Brightness
  0.76,  // Brightness
  0.77,  // Brightness
  0.78,  // Brightness
  0.79,  // Brightness
  0.8,  // Brightness
  0.81,  // Brightness
  0.82,  // Brightness
  0.83,  // Brightness
  0.84,  // Brightness
  0.85,  // Brightness
  0.85,  // Brightness
  0.86,  // Brightness
  0.87,  // Brightness
  0.87,  // Brightness
  0.88,  // Brightness
  0.88,  // Brightness
  0.88,  // Brightness
  0.89,  // Brightness
  0.89,  // Brightness
  0.89,  // Brightness
  0.89,  // Brightness
  0.89,  // Brightness
  0.89,  // Brightness
  0.89,  // Brightness
  0.89,  // Brightness
  0.89,  // Brightness
  0.88,  // Brightness
  0.88,  // Brightness
  0.88,  // Brightness
  0.87,  // Brightness
  0.87,  // Brightness
  0.86,  // Brightness
  0.85,  // Brightness
  0.85,  // Brightness
  0.84,  // Brightness
  0.83,  // Brightness
  0.82,  // Brightness
  0.81,  // Brightness
  0.8,  // Brightness
  0.79,  // Brightness
  0.78,  // Brightness
  0.77,  // Brightness
  0.75,  // Brightness
  0.74,  // Brightness
  0.73,  // Brightness
  0.71,  // Brightness
  0.7,  // Brightness
  0.69,  // Brightness
  0.67,  // Brightness
  0.65,  // Brightness
  0.64,  // Brightness
  0.62,  // Brightness
  0.61,  // Brightness
  0.59,  // Brightness
  0.57,  // Brightness
  0.55,  // Brightness
  0.54,  // Brightness
  0.52,  // Brightness
  0.5,  // Brightness
  0.48,  // Brightness
  0.46,  // Brightness
  0.44,  // Brightness
  0.43,  // Brightness
  0.41,  // Brightness
  0.39,  // Brightness
  0.37,  // Brightness
  0.35,  // Brightness
  0.33,  // Brightness
  0.31,  // Brightness
  0.29,  // Brightness
  0.27,  // Brightness
  0.25,  // Brightness
  0.23,  // Brightness
  0.21,  // Brightness
  0.19,  // Brightness
  0.17,  // Brightness
  0.15,  // Brightness
  0.13,  // Brightness
  0.11,  // Brightness
  0.1,  // Brightness
  0.08,  // Brightness
  0.06,  // Brightness
  0.04,  // Brightness
  0.02,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
  0.0,  // Brightness
};


void setup() {
  pixels.begin();
  pixels.show(); // Initialize all pixels to 'off'
}

void loop() {
  for (int i = 0; i < sizeof(rgbValues) / sizeof(rgbValues[0]); i++) {
    int r = rgbValues[i][0];
    int g = rgbValues[i][1];
    int b = rgbValues[i][2];
    
    // Set brightness (using a simple map function)
    int brightness = map(brightnessValues[i] * 255, 0, 255, 0, BRIGHTNESS);
    
    // Update the pixels
    setPixelColor(5, r, g, b, brightness);
    setPixelColor(6, r, g, b, brightness);
    setPixelColor(7, r, g, b, brightness);
    
    pixels.show();
    delay(200); // Wait for 200 milliseconds
  }
  
  // Turn off the pixels after the loop
  pixels.fill(pixels.Color(0, 0, 0));
  pixels.show();
  while (true); // Stop the loop
}

void setPixelColor(int pixel, int r, int g, int b, int brightness) {
  // Set pixel color with brightness
  r = (r * brightness) / 255;
  g = (g * brightness) / 255;
  b = (b * brightness) / 255;
  
  pixels.setPixelColor(pixel, pixels.Color(r, g, b));
}
