import paho.mqtt.client as mqtt
import time
import random
import json
import requests # Importamos a nova biblioteca

# --- Configurações da API OpenWeatherMap ---
API_KEY = "c98bc5acbfe9460aead8c017e033c644"
CIDADE = "Ibipora,BR" # Cidade para buscar a previsão do tempo. Pode alterar!
API_URL = f"https://api.openweathermap.org/data/2.5/weather?q={CIDADE}&appid={API_KEY}&units=metric&lang=pt_br"

# --- Configurações MQTT (continuam as mesmas) ---
BROKER = "broker.hivemq.com"
PORT = 1883
TOPICO_COMANDO = "sensor_rio/renan/comando"
TOPICO_NIVEL = "sensor_rio/renan/nivel"

# --- Funções de Callback do MQTT (continuam as mesmas) ---
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Conectado ao Broker MQTT!")
        client.subscribe(TOPICO_NIVEL)
    else:
        print(f"Falha ao conectar, código de erro: {rc}\n")

def on_message(client, userdata, msg):
    print(f"Nível do rio recebido do ESP32: {msg.payload.decode()} mm")

def get_real_weather():
    """Busca a previsão do tempo real na API e decide se está chovendo."""
    print(f"\nBuscando previsão do tempo para {CIDADE}...")
    try:
        response = requests.get(API_URL)
        # Verifica se a requisição foi bem sucedida
        if response.status_code == 200:
            data = response.json()
            weather_main = data['weather'][0]['main']
            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']
            
            print(f"Previsão recebida: {weather_desc.capitalize()} ({temp}°C)")
            
            # Condições consideradas como chuva
            rainy_conditions = ["Rain", "Thunderstorm", "Drizzle", "Snow"]
            
            if weather_main in rainy_conditions:
                return True # Está chovendo
            else:
                return False # Não está chovendo
        else:
            print(f"Erro ao buscar dados da API: Status {response.status_code}")
            return None # Retorna None em caso de erro

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão com a API: {e}")
        return None

# --- Lógica Principal ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_start()

print("Script de monitoramento iniciado (API Real). Pressione Ctrl+C para parar.")

try:
    while True:
        is_rainy = get_real_weather()
        
        # Só executa se a chamada à API foi bem sucedida
        if is_rainy is not None:
            if is_rainy:
                rain_rate = round(random.uniform(5.0, 20.0), 2)
                command = {"action": "start_rain", "rate": rain_rate}
                print(f"🌦️  DECISÃO: Chuva detectada! Enviando comando para aumentar o rio em {rain_rate} mm/min.")
            else:
                command = {"action": "stop_rain"}
                print(f"☀️  DECISÃO: Tempo estável. Enviando comando para estabilizar o rio.")
            
            client.publish(TOPICO_COMANDO, json.dumps(command))
        
        # Espera 10 minutos para a próxima verificação (API tem limites de chamadas)
        print("\nAguardando 10 minutos (600s) para a próxima verificação...")
        time.sleep(600)

except KeyboardInterrupt:
    print("\nEncerrando o script...")
finally:
    client.loop_stop()
    client.disconnect()