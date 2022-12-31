#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define LED_PIN D6
#define LED_COUNT 60

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
 uint32_t r = strip.Color(255,0,0);
 uint32_t g = strip.Color(0,255,0);
 uint32_t y = strip.Color(255,255,0);
 uint32_t b = strip.Color(0,0,255);

 // arrays of the routes - some of which are backwards
 int route1[30] = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,34,33,32,31,30,29,28,27,26,25};
 int route32x[30] = {55,56,57,58,59,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,24,23,22,21,20};
 int route29[20] = {54,53,52,51,50,49,48,47,46,45,44,43,42,41,40,39,38,37,36,35};

// Update these with values suitable for your network.
const char* ssid = "";
const char* password = "";
const char* mqtt_server = "";
const char* mqtt_user = "";
const char* mqtt_pass = "";

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE  (50)
char msg[MSG_BUFFER_SIZE];
int value = 0;

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  static StaticJsonDocument<256> json_doc;
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  strip.clear();
  // Deserialize the JSON document
  DeserializationError error = deserializeJson(json_doc, payload);

  if (error) {
    Serial.print(F("deserializeJson() failed: "));
    Serial.println(error.f_str());
    return;
  }
  
  JsonArray pos;
  int count;
  bool stoparray;
  
  pos = json_doc["32x"];
  int tpos32x;
  int tpos32x_check[5];
  int tpos32x_counter = 0;
  int tpos;
  int tpos1;
  count = sizeof(pos);
  Serial.println(count);
  stoparray = false;
  for (int i = 0; i < count; i++) {
    tpos32x = pos[i];
    if (tpos32x > 0) {
      stoparray = true;
      }
    if (tpos32x == 0 and (i == 0 or stoparray)) {
      break;
    }
    strip.setPixelColor(route32x[tpos32x], g);
    // Keep a record of the lights we have lit up for the 32x
    // in case they collide with a number 1
    tpos32x_check[tpos32x_counter] = route32x[tpos32x];
    tpos32x_counter++;
    strip.show();
  }

  pos = json_doc["1"];
  count = sizeof(pos);
  Serial.println(count);
  stoparray = false;
  bool yellow;
  for (int i = 0; i < count; i++) {
    yellow = false;
    tpos1 = pos[i];
    if (tpos1 > 0) {
      stoparray = true;
      }
    if (tpos1 == 0 and (i == 0 or stoparray)) {
      break;
    }
    // if tpos32x and tpos1 collide, set to yellow
    for (int tx = 0; tx < 5; tx++) {
      Serial.println("Checking for yellow");
      Serial.println(tpos32x_check[tx]);
      Serial.println(route1[tpos1]);
      if (tpos32x_check[tx] == route1[tpos1]) {
        yellow = true;
      }
    }
    // Set the light to yellow if 1 and 32x are in the same place
    if (yellow) {
      Serial.println("Setting to yellow");
      strip.setPixelColor(route1[tpos1], y);
    }
    // Just a number 1 bus at this point, so set the light to red
    else {
      strip.setPixelColor(route1[tpos1], r);
    }
    strip.show();
  }

  // The simple version is for bus 29 - no overlaps on this route
  pos = json_doc["29"];
  count = sizeof(pos);
  Serial.println(count);
  stoparray = false;
  for (int i = 0; i < count; i++) {
    tpos = pos[i];
    if (tpos > 0) {
      stoparray = true;
      }
    if (tpos == 0 and (i == 0 or stoparray)) {
      break;
    }
    strip.setPixelColor(route29[tpos], b);
    strip.show();
  }
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str(),mqtt_user,mqtt_pass)) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("bus/board_alive", "hello world");
      // ... and resubscribe
      client.subscribe("bus/positions");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void test_strips(){
  int wait = 10;
  strip.clear();
  // Number 29
  for(int i=0; i<20; i++) { // For each pixel in strip...
    strip.setPixelColor(route29[i], b);         //  Set pixel's color (in RAM)
    strip.show();                          //  Update strip to match
    delay(wait);                           //  Pause for a moment
  }

  // Number 1
  strip.clear();
  for(int i=0; i<30; i++) { // For each pixel in strip...
    strip.setPixelColor(route1[i], r);         //  Set pixel's color (in RAM)
    strip.show();                          //  Update strip to match
    delay(wait);                           //  Pause for a moment
  }
  
  // Number 32x
  strip.clear();
  for(int i=0; i<30; i++) { // For each pixel in strip...
    strip.setPixelColor(route32x[i], g);         //  Set pixel's color (in RAM)
    strip.show();                          //  Update strip to match
    delay(wait);                           //  Pause for a moment
  }
  strip.clear();
}

void setup() {
 // initialize serial:
 Serial.begin(9600); 
 strip.begin(); //always needed
 strip.show(); // 0 data => off.
 strip.setBrightness(20); // ~20% (max = 255
 strip.clear();
 test_strips();
 strip.show();
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 2000) {
    lastMsg = now;
    ++value;
    if (value > 20) {
      value = 0;
    }
    snprintf (msg, MSG_BUFFER_SIZE, "poo #%ld", value);
    Serial.print("Publish message: ");
    Serial.println(msg);
    client.publish("bus/board_alive", msg);
  }
}

 