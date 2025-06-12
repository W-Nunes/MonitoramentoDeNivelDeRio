import streamlit as st
import time
import pandas as pd
import json
import requests
import paho.mqtt.client as mqtt
from datetime import datetime
import pickle
import random
import sqlite3

# --- CONFIGURAÇÕES GLOBAIS ---
DB_FILE = "dados_rio.db"
MODEL_FILE = "modelo_enchente.pkl"
API_KEY = "c98bc5acbfe9460aead8c017e033c644"
LAT, LON = 19.4326, -99.1332 # Coordenadas de um local para teste (Cidade do México)
API_URL = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric&lang=pt_br"
FORECAST_URL = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
BROKER = "broker.hivemq.com"
PORT = 1883
TOPICO_COMANDO = "sensor_rio/renan/comando"

# --- FUNÇÕES DE BACKEND ---
def get_real_weather():
    """Busca a condição atual e a probabilidade de chuva."""
    try:
        current_response = requests.get(API_URL)
        forecast_response = requests.get(FORECAST_URL)
        if current_response.status_code == 200 and forecast_response.status_code == 200:
            current_data = current_response.json()
            forecast_data = forecast_response.json()
            return {
                "condicao_main": current_data['weather'][0]['main'], # Ex: 'Rain', 'Clouds', 'Clear'
                "prob_chuva": forecast_data['list'][0].get('pop', 0),
                "vento_kmh": current_data['wind']['speed'] * 3.6,
                "descricao": current_data['weather'][0]['description'].capitalize()
            }
        else:
            return None
    except Exception:
        return None

def get_latest_reading_from_db():
    """Busca a última leitura de nível do rio do banco de dados."""
    try:
        conn = sqlite3.connect(f'file:{DB_FILE}?mode=ro', uri=True)
        # Usamos uma query para pegar a última linha inserida
        query = "SELECT nivel_mm FROM leituras WHERE id = (SELECT MAX(id) FROM leituras)"
        data = pd.read_sql_query(query, conn)
        conn.close()
        return data['nivel_mm'].iloc[0] if not data.empty else None
    except Exception:
        return None

# --- CARREGAMENTO DO MODELO E CLIENTE MQTT ---
try:
    with open(MODEL_FILE, 'rb') as file:
        flood_model = pickle.load(file)
except FileNotFoundError:
    st.error(f"Arquivo do modelo '{MODEL_FILE}' não encontrado!")
    st.info("Execute 'treinar_modelo.py' primeiro.")
    st.stop()

if 'mqtt_client' not in st.session_state:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    try:
        client.connect(BROKER, PORT, 60)
        st.session_state.mqtt_client = client
    except Exception as e:
        st.error(f"Erro ao conectar ao MQTT: {e}")

# --- APLICAÇÃO STREAMLIT ---
st.set_page_config(page_title="Dashboard Preditivo de Enchente", page_icon="🌊", layout="wide")
st.title("🌊 Dashboard Preditivo de Risco de Enchente")

nivel_atual = get_latest_reading_from_db()
st.metric("Nível Atual da Água 💧", value=f"{nivel_atual:.2f} mm" if nivel_atual is not None else "Aguardando dados...")

if st.button("Executar Análise Preditiva e Comandar Simulação"):
    with st.spinner("Analisando..."):
        weather_data = get_real_weather()
        nivel_rio_atual = get_latest_reading_from_db()

    if weather_data and nivel_rio_atual is not None:
        
        # =================================================================
        # >>> LÓGICA DE DECISÃO FINAL E CORRIGIDA <<<
        # =================================================================
        
        st.write("---")
        st.write(f"**Condição Climática Atual:** {weather_data['descricao']}")

        rainy_conditions = ["Rain", "Thunderstorm", "Drizzle", "Snow"]
        is_weather_rainy = weather_data['condicao_main'] in rainy_conditions
        
        command_to_send = None

        if not is_weather_rainy:
            # REGRA 1: Se o tempo NÃO é chuvoso, o comando é sempre parar a chuva.
            st.success("**DECISÃO: TEMPO ESTÁVEL.**")
            command_to_send = {"action": "stop_rain"}
        else:
            # REGRA 2: Se o tempo é chuvoso, usamos o modelo de ML para definir a INTENSIDADE.
            st.info("**DECISÃO: TEMPO CHUVOSO. EXECUTANDO MODELO PREDITIVO...**")
            
            input_data = pd.DataFrame([[weather_data['prob_chuva'], weather_data['vento_kmh'], nivel_rio_atual]], columns=['prob_chuva', 'vento_kmh', 'nivel_rio_mm'])
            prediction = flood_model.predict(input_data)[0]
            prediction_proba = flood_model.predict_proba(input_data)[0][1]
            
            st.write("**Dados de Entrada para o Modelo:**"); st.dataframe(input_data)
            st.write("**Resultado do Modelo Preditivo:**")

            if prediction == 1:
                # REGRA 3: Risco Alto = Chuva Forte
                st.error(f"**PREDIÇÃO: RISCO ALTO DE ENCHENTE** (Confiança: {prediction_proba*100:.1f}%)")
                command_to_send = {"action": "start_rain", "rate": random.uniform(25.0, 40.0)}
            else:
                # REGRA 4: Risco Baixo = Chuva Fraca
                st.warning(f"**PREDIÇÃO: RISCO BAIXO DE ENCHENTE** (Confiança: {(1-prediction_proba)*100:.1f}%)")
                command_to_send = {"action": "start_rain", "rate": random.uniform(1.0, 5.0)}
        
        # Envia o comando definido pela lógica acima
        if command_to_send and 'mqtt_client' in st.session_state:
            st.session_state.mqtt_client.publish(TOPICO_COMANDO, json.dumps(command_to_send))
            st.info(f"Comando enviado para o ESP32 via MQTT: `{json.dumps(command_to_send)}`")
            
    else:
        st.error("Não foi possível obter todos os dados necessários para a análise.")

# Lógica de atualização da página
time.sleep(5)
st.rerun()