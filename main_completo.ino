#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// --- Configurações de Rede e MQTT ---
const char* ssid = "Wokwi-GUEST"; // Rede WiFi do Wokwi. Deve ser esta.
const char* password = "";        // Senha em branco para a rede do Wokwi.
const char* mqtt_server = "broker.hivemq.com"; // Servidor MQTT público para teste

// --- Tópicos MQTT (Canais de Comunicação) ---
const char* topico_nivel_rio = "sensor_rio/renan/nivel"; // Canal para ENVIAR o nível do rio
const char* topico_comando_chuva = "sensor_rio/renan/comando"; // Canal para RECEBER comandos

// --- Variáveis Globais ---
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
float waterLevel_mm = 500.0;
bool isRaining = false;
float rainRate_mm_per_min = 0.0;
unsigned long lastRainSimTime = 0;

// --- Função Chamada ao Receber Mensagem MQTT ---
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Mensagem recebida no tópico: ");
  Serial.println(topic);

  // Converte o payload para String
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  // Interpreta o JSON recebido
  JsonDocument doc;
  deserializeJson(doc, message);
  const char* action = doc["action"];

  if (strcmp(action, "start_rain") == 0) {
    isRaining = true;
    rainRate_mm_per_min = doc["rate"];
    lastRainSimTime = millis();
    Serial.println("Comando de chuva recebido via MQTT!");
  } else if (strcmp(action, "stop_rain") == 0) {
    isRaining = false;
    Serial.println("Comando para parar chuva recebido via MQTT.");
  }
}

// --- Função para Reconectar ao MQTT ---
void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentando conectar ao MQTT...");
    if (client.connect("ESP32_Rio_Client_Renan")) {
      Serial.println("conectado!");
      // Se inscreve no tópico de comandos para poder receber mensagens
      client.subscribe(topico_comando_chuva);
    } else {
      Serial.print("falhou, rc=");
      Serial.print(client.state());
      Serial.println(" tentando novamente em 5 segundos");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("Iniciando...");

  // Conecta ao WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");
  Serial.print("Endereço IP: ");
  Serial.println(WiFi.localIP());

  // Configura o servidor e a função de callback do MQTT
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop(); // Essencial para manter a conexão e receber mensagens

  // Simula o aumento do nível da água se estiver chovendo
  if (isRaining) {
    unsigned long currentTime = millis();
    if (currentTime - lastRainSimTime >= 1000) {
      float increasePerSecond = rainRate_mm_per_min / 60.0;
      waterLevel_mm += increasePerSecond;
      lastRainSimTime = currentTime;
    }
  }

  // Publica o nível da água a cada 5 segundos
  unsigned long now = millis();
  if (now - lastMsg > 5000) {
    lastMsg = now;
    String nivel_formatado = String(waterLevel_mm, 2);
    Serial.print("Publicando nível do rio: ");
    Serial.println(nivel_formatado);
    
    // Envia a mensagem para o tópico MQTT
    client.publish(topico_nivel_rio, nivel_formatado.c_str());
  }
}