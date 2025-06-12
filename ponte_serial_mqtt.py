import serial
import time
import paho.mqtt.client as mqtt

# --- CONFIGURAÇÕES ---
# Lembre-se de descobrir e colocar a porta COM correta aqui!
PORTA_SERIAL_WOKWI = 'COM3' 
BAUD_RATE = 115200
BROKER_MQTT = "broker.hivemq.com"
PORT_MQTT = 1883
TOPICO_NIVEL = "sensor_rio/renan/nivel"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Ponte conectada ao Broker MQTT com sucesso!")
    else:
        print(f"Falha ao conectar ao MQTT, código {rc}")

# Inicializa o cliente MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
try:
    mqtt_client.connect(BROKER_MQTT, PORT_MQTT, 60)
    mqtt_client.loop_start()
except Exception as e:
    print(f"Erro ao conectar ao MQTT: {e}")
    exit()

# Inicializa a conexão Serial
try:
    ser = serial.Serial(PORTA_SERIAL_WOKWI, BAUD_RATE, timeout=1)
    print(f"Ponte conectada à porta serial {PORTA_SERIAL_WOKWI}")
except serial.SerialException as e:
    print(f"Erro ao abrir a porta serial: {e}")
    print("Verifique se a simulação do Wokwi está rodando e se a porta COM está correta.")
    mqtt_client.loop_stop()
    exit()

print("--- Ponte Serial-MQTT iniciada. Lendo dados do ESP32 e publicando... ---")

try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            
            # Se a linha contiver a informação que queremos
            if line.startswith("nivel_rio:"):
                nivel = line.split(":")[1]
                print(f"Dado recebido do ESP32: {nivel} mm. Publicando no MQTT...")
                # Publica o dado no tópico MQTT
                mqtt_client.publish(TOPICO_NIVEL, nivel)
            else:
                # Imprime outras mensagens do ESP32 (para depuração)
                if line:
                    print(f"ESP32 diz: {line}")
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nEncerrando a ponte.")
finally:
    ser.close()
    mqtt_client.loop_stop()
    mqtt_client.disconnect()