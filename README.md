🌊 Sistema Preditivo de Risco de Enchente
1. Visão Geral
Este projeto é um sistema completo de Internet das Coisas (IoT) e Inteligência Artificial, projetado para monitorar o nível de rios, prever riscos de enchentes e simular o impacto de chuvas em tempo real.
O propósito fundamental é servir como um protótipo para uma rede de sensores que pode ser replicada e distribuída ao longo de uma bacia hidrográfica. Ao coletar dados de múltiplos pontos, o sistema centraliza as informações em um dashboard interativo, permitindo que autoridades e a defesa civil tomem decisões proativas, se preparem e mitiguem os danos de eventuais cheias e enchentes.
A solução integra desde a simulação de hardware de baixo nível até a aplicação de um modelo de Machine Learning e a visualização de dados em uma interface web amigável.
2. Arquitetura do Sistema
A solução é composta por múltiplos componentes desacoplados que se comunicam através de um broker MQTT e um banco de dados local, garantindo robustez e escalabilidade.
 * Simulador de Sensor (ESP32 + Wokwi):
   * Um microcontrolador ESP32 é simulado no ambiente Wokwi, lendo dados de um sensor ultrassônico para medir o nível da água.
   * Ele se conecta a uma rede WiFi e publica o nível do rio em um tópico MQTT (sensor_rio/renan/nivel) a cada 5 segundos.
   * Ao mesmo tempo, ele escuta um tópico de comando (sensor_rio/renan/comando) para receber instruções de simulação de chuva.
 * Coletor de Dados (mqtt_coletor_db.py):
   * Um script Python robusto que se inscreve no tópico MQTT sensor_rio/renan/nivel.
   * Sua única função é ouvir as publicações do ESP32 e salvar cada leitura de nível do rio em um banco de dados SQLite (dados_rio.db), criando um histórico persistente.
 * Dashboard Preditivo (dashboard.py):
   * A interface principal do sistema, construída com Streamlit.
   * Ele lê os dados históricos e atuais do nível do rio diretamente do banco de dados dados_rio.db.
   * Ao comando do usuário, ele executa um modelo de Machine Learning (Scikit-learn) treinado, usando a probabilidade de chuva (da API) e o nível atual do rio (do DB) para prever o risco de enchente.
   * Exibe os dados, gráficos e alertas de risco de forma clara para o usuário.
3. Tecnologias Utilizadas
Hardware Simulado
 * Microcontrolador: ESP32 DevKit V1
 * Sensor: Sensor Ultrassônico HC-SR04
 * Ambiente de Simulação: Wokwi for VS Code
Software & Frameworks
 * IDE: Visual Studio Code
 * Build System (Embarcado): PlatformIO
 * Framework de Dashboard: Streamlit
 * Banco de Dados: SQLite 3
Linguagens
 * Python 3.x: Para toda a lógica de backend, coleta, treinamento e dashboard.
 * C++ (Arduino Framework): Para a programação do microcontrolador ESP32.
Bibliotecas Python Principais
 * paho-mqtt: Para comunicação com o broker MQTT.
 * requests: Para realizar chamadas à API de previsão do tempo.
 * pandas: Para manipulação e preparação dos dados para o modelo.
 * scikit-learn: Para treinar e executar o modelo de classificação (RandomForestClassifier).
 * streamlit: Para a criação do dashboard web interativo.
 * sqlite3: Para interação com o banco de dados.
Protocolos
 * MQTT: Protocolo leve de mensagens, ideal para comunicação IoT entre os componentes.
APIs Externas
 * OpenWeatherMap: Fornece dados de previsão do tempo em tempo real.
4. Como Executar o Sistema
Para executar o projeto, você precisará de 3 terminais rodando simultaneamente.
Pré-requisitos
 * Garanta que o Python 3 e o VS Code com a extensão PlatformIO estejam instalados.
 * Instale todas as bibliotecas Python necessárias com um único comando:
   pip install streamlit pandas scikit-learn paho-mqtt requests

Passo 1: Treinar o Modelo (Executar Apenas Uma Vez)
Antes de tudo, você precisa criar o dataset e treinar o modelo de Machine Learning.
 * Execute o script de geração de dados:
   python gerar_dados.py

 * Execute o script de treinamento:
   python treinar_modelo.py

   Isso criará o arquivo modelo_enchente.pkl, que será usado pelo dashboard.
Passo 2: Iniciar a Simulação do Sensor (Terminal 1)
 * No VS Code, abra o menu do PlatformIO (ícone 🐜).
 * Clique em Build para compilar o código do ESP32.
 * Após o sucesso, inicie a simulação com o comando da paleta (Ctrl+Shift+P): Wokwi: Start Simulator.
 * (Opcional) Abra o Monitor do PlatformIO para ver os logs do ESP32.
Passo 3: Iniciar o Coletor de Dados (Terminal 2)
 * Abra um novo terminal no VS Code.
 * Execute o script que salva os dados do rio no banco de dados:
   python mqtt_coletor_db.py

   Este terminal ficará ativo, mostrando os dados que estão sendo recebidos e salvos.
Passo 5: Iniciar o Dashboard (Navegador)
 * Abra um quarto terminal (ou use o terminal 3 após iniciar o controlador).
 * Execute o dashboard Streamlit:
   streamlit run dashboard.py

 * Abra o endereço http://localhost:8501 no seu navegador para interagir com o sistema.
5. Estrutura dos Arquivos
   
.
├── src/main.ino                # Código do ESP32: publica nível e reage a comandos
├── gerar_dados.py              # Script para criar o dataset de treinamento
├── treinar_modelo.py           # Script que treina e salva o modelo de ML
├── mqtt_coletor_db.py          # Coleta dados do MQTT e salva no SQLite
├── dashboard.py                # Aplicação principal do Streamlit
├── modelo_enchente.pkl         # Arquivo do modelo de ML treinado
├── dados_enchente.csv          # Dataset gerado para o treinamento
├── dados_rio.db                # Banco de dados com as leituras em tempo real
├── platformio.ini              # Configuração do projeto PlatformIO
├── wokwi.toml                  # Configuração da simulação Wokwi
└── diagram.json                # Definição do circuito eletrônico simulado

6. Próximos Passos e Melhorias
 * Hardware Real: Substituir a simulação do Wokwi por um ESP32 e um sensor HC-SR04 físicos.
 * Escalabilidade: Adaptar os scripts para receber dados de múltiplos sensores, cada um com um ID único em seu tópico MQTT.
 * Dataset Robusto: Coletar dados históricos reais da bacia hidrográfica para treinar um modelo mais preciso.
 * Deployment na Nuvem: Publicar o dashboard Streamlit na nuvem (ex: Streamlit Community Cloud, Heroku) para acesso remoto.
 * Alertas Ativos: Integrar um serviço de envio de notificações (SMS, Telegram, Email) para alertar as autoridades quando o modelo prever um risco alto.
