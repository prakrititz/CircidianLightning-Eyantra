
#include <ESP8266WiFi.h> // for ESP8266
#include <ESP8266WebServer.h> // for ESP8266
//#include <ESPWifi.h> //for ESP32
//#include <ESPWebServer.h> //for ESP32
#include <Adafruit_NeoPixel.h>
#include <ESPmDNS.h> // mDNS library for ESP32/ESP8266

#define PIN 7 // Pin where NeoPixel is connected
#define NUMPIXELS 12 // Number of pixels on the strip

const char* ssid = "Network";    // Replace with your WiFi SSID
const char* password = "qwertyui";  // Replace with your WiFi Password


Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
ESP8266WebServer server(80);

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

  // Initialize mDNS
  if (MDNS.begin("esplight")) {
    Serial.println("mDNS responder started");
    Serial.print("Access your ESP32 at http://");
    Serial.print("esplight");
    Serial.println(".local");
  } else {
    Serial.println("Error setting up mDNS responder!");
  }

  pixels.begin();  // Initialize NeoPixel strip
  
  // Define routes
  server.on("/set_color", HTTP_POST, handleSetColor);
  
  // Start the server
  server.begin();
  Serial.println("HTTP server started"); 
}

void loop() {
  server.handleClient();  // Handle incoming clients
  //MDNS.update();          // Handle mDNS queries
}
