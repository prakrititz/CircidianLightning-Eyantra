#include <WiFi.h>
#include <WebServer.h>
#include <Adafruit_NeoPixel.h>

#define PIN 13 // Pin where NeoPixel is connected
#define NUMPIXELS 12 // Number of pixels on the strip

const char* ssid = "Network";    // Replace with your WiFi SSID
const char* password = "qwertyui";  // Replace with your WiFi Password

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
WebServer server(80);

// Function to set color and brightness
void setNeoPixelColor(int r, int g, int b, float brightness) {
  uint32_t color = pixels.Color(r * brightness, g * brightness, b * brightness);
  for (int i = 0; i < NUMPIXELS; i++) {
    pixels.setPixelColor(i, color);
  }
  pixels.show();
}

// Handle POST requests to change LED values
void handleSetColor() {
  if (server.hasArg("R") && server.hasArg("G") && server.hasArg("B") && server.hasArg("Brightness")) {
    int r = server.arg("R").toInt();
    int g = server.arg("G").toInt();
    int b = server.arg("B").toInt();
    float brightness = server.arg("Brightness").toFloat();
    setNeoPixelColor(r, g, b, brightness);
    server.send(200, "text/plain", "Color Set");
  } else {
    server.send(400, "text/plain", "Invalid Request");
  }
}

void setup() {
  Serial.begin(115200);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  pixels.begin();  // Initialize NeoPixel strip
  
  // Define routes
  server.on("/set_color", HTTP_POST, handleSetColor);
  
  // Start the server
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();  // Handle incoming clients
}
