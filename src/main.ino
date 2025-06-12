#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

const int TRIG_PIN = 5;
const int ECHO_PIN = 18;

const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.hivemq.com";
const char* topico_nivel_rio = "sensor_rio/renan/nivel";
const char* topico_comando_chuva = "sensor_rio/renan/comando";

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
float waterLevel_mm = 500.0;
bool isRaining = false;
float rainRate_mm_per_min = 0.0;
unsigned long lastRainSimTime = 0;

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Comando MQTT recebido. Processando... ");

  JsonDocument doc;
  DeserializationError error = deserializeJson(doc, payload, length);

  if (error) {
    Serial.print("deserializeJson() falhou: ");
    Serial.println(error.c_str());
    return;
  }

  const char* action = doc["action"];
  if (action) {
    if (strcmp(action, "start_rain") == 0) {
      isRaining = true;
      rainRate_mm_per_min = doc["rate"] | 15.0; // Pega a taxa ou usa 15.0 como padrão
      lastRainSimTime = millis();
      Serial.println("OK. -> INICIANDO CHUVA.");
    } else if (strcmp(action, "stop_rain") == 0) {
      isRaining = false;
      Serial.println("OK. -> PARANDO CHUVA.");
    }
  } else {
    Serial.println("ERRO: JSON recebido sem a chave 'action'.");
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentando conectar ao MQTT...");
    String clientId = "ESP32-Rio-Final-" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println(" Conectado!");
      client.subscribe(topico_comando_chuva);
    } else {
      Serial.print(" falhou, rc=");
      Serial.print(client.state());
      Serial.println(" tentando novamente em 5s");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  Serial.println("\nConectando ao WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");
  
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (isRaining) {
    unsigned long currentTime = millis();
    if (currentTime - lastRainSimTime >= 1000) {
      waterLevel_mm += (rainRate_mm_per_min / 60.0);
      lastRainSimTime = currentTime;
    }
  }

  unsigned long now = millis();
  if (now - lastMsg > 5000) {
    lastMsg = now;
    String nivel_formatado = String(waterLevel_mm, 2);
    Serial.print("Publicando nivel: ");
    Serial.println(nivel_formatado);
    client.publish(topico_nivel_rio, nivel_formatado.c_str());
  }
}