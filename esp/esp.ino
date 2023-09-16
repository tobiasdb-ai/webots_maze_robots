#include <ESP8266WiFi.h>
#include <PubSubClient.h>

bool isShutDown = 0;

#define buttonPin 4
#define rightLed 14
#define upLed 15
#define downLed 12
#define leftLed 13


const char* ssid = "NAME";
const char* password = "PASS";
const char* mqtt_server = "IP";

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE	(50)
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
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
  if ((char)payload[0] == 'N') {
    digitalWrite(upLed, HIGH);   
    digitalWrite(rightLed, LOW);
    digitalWrite(downLed, LOW); 
    digitalWrite(leftLed, LOW); 
  } else if ((char)payload[0] == 'E'){
    digitalWrite(upLed, LOW);   
    digitalWrite(rightLed, HIGH);
    digitalWrite(downLed, LOW); 
    digitalWrite(leftLed, LOW); 
  } else if ((char)payload[0] == 'S'){
    digitalWrite(upLed, LOW);   
    digitalWrite(rightLed, LOW);
    digitalWrite(downLed, HIGH); 
    digitalWrite(leftLed, LOW); 
  } else if ((char)payload[0] == 'W'){
    digitalWrite(upLed, LOW);   
    digitalWrite(rightLed, LOW);
    digitalWrite(downLed, LOW); 
    digitalWrite(leftLed, HIGH); 
  } else {
    digitalWrite(upLed, LOW);   
    digitalWrite(rightLed, LOW);
    digitalWrite(downLed, LOW); 
    digitalWrite(leftLed, LOW);
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
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      // ... and resubscribe
      client.subscribe("bot1/direction");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}


void ICACHE_RAM_ATTR isr() {
  isShutDown = true;
  digitalWrite(leftLed, LOW);
  digitalWrite(rightLed, LOW);
  digitalWrite(upLed, LOW);
  digitalWrite(downLed, LOW);
  client.publish("bot1/direction", "X");
  client.publish("bot2/direction", "X");
  client.publish("bot3/direction", "X");
  client.publish("bot4/direction", "X");
  client.publish("noodstop", "Y");
}

void setup() {
  pinMode(leftLed, OUTPUT);
  pinMode(downLed, OUTPUT);
  pinMode(upLed, OUTPUT);
  pinMode(rightLed, OUTPUT);
  pinMode(D2, INPUT);
  pinMode(BUILTIN_LED, OUTPUT);
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  digitalWrite(BUILTIN_LED, HIGH);
  attachInterrupt(D2,isr, CHANGE);
}

void loop() {

  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}