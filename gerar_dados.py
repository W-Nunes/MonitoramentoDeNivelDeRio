# gerar_dados.py
import pandas as pd
import numpy as np

# Número de amostras de dados que vamos gerar
NUM_SAMPLES = 2000

# Gerando dados base aleatórios
data = {
    'prob_chuva': np.random.rand(NUM_SAMPLES), # Probabilidade de 0 a 1
    'vento_kmh': np.random.uniform(0, 40, NUM_SAMPLES), # Vento de 0 a 40 km/h
    'nivel_rio_mm': np.random.uniform(300, 800, NUM_SAMPLES) # Nível do rio de 300 a 800 mm
}

df = pd.DataFrame(data)

# Aplicando regras para criar a variável alvo 'risco_enchente' (1 para Sim, 0 para Não)
# Esta é a nossa "verdade" que o modelo tentará aprender
conditions = [
    (df['prob_chuva'] > 0.75) & (df['vento_kmh'] > 20) & (df['nivel_rio_mm'] > 650),
    (df['prob_chuva'] > 0.6) & (df['nivel_rio_mm'] > 700),
    (df['prob_chuva'] > 0.8),
    (df['vento_kmh'] > 30) & (df['nivel_rio_mm'] > 600)
]

# Definimos que qualquer uma das condições acima resulta em risco de enchente
df['risco_enchente'] = np.where(np.logical_or.reduce(conditions), 1, 0)

# Salvando os dados em um arquivo CSV
df.to_csv('dados_enchente.csv', index=False)

print(f"Arquivo 'dados_enchente.csv' com {NUM_SAMPLES} amostras foi criado com sucesso!")
print(f"Total de casos de enchente gerados: {df['risco_enchente'].sum()}")