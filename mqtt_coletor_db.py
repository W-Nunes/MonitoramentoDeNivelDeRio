import paho.mqtt.client as mqtt
import sqlite3
import time
from datetime import datetime

# --- CONFIGURAÇÕES ---
BROKER = "broker.hivemq.com"
PORT = 1883
TOPICO_NIVEL = "sensor_rio/renan/nivel"
DB_FILE = "dados_rio.db"

def setup_database():
    """Cria o banco de dados e a tabela se não existirem."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            nivel_mm REAL
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Banco de dados '{DB_FILE}' pronto.")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Coletor conectado ao Broker MQTT!")
        client.subscribe(TOPICO_NIVEL)
        print(f"Inscrito no tópico: {TOPICO_NIVEL}")
    else:
        print(f"Falha ao conectar ao MQTT, código {rc}")

def on_message(client, userdata, msg):
    """Função chamada quando uma mensagem chega do ESP32."""
    try:
        nivel = float(msg.payload.decode())
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO leituras (nivel_mm) VALUES (?)", (nivel,))
        conn.commit()
        conn.close()
        timestamp_atual = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp_atual}] Dado recebido e salvo no DB: {nivel:.2f} mm")
    except Exception as e:
        print(f"Erro ao processar mensagem ou salvar no DB: {e}")

def main():
    setup_database()
    
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
    except Exception as e:
        print(f"Erro fatal ao conectar no MQTT: {e}")
        return
        
    print("--- Coletor MQTT para Banco de Dados iniciado. Aguardando dados... ---")
    # loop_forever() é um loop bloqueante que mantém o script rodando para escutar
    client.loop_forever()

if __name__ == "__main__":
    main()