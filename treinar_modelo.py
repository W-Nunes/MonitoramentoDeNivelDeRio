# treinar_modelo.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle

print("Iniciando o treinamento do modelo...")

# Carregar os dados gerados
try:
    df = pd.read_csv('dados_enchente.csv')
except FileNotFoundError:
    print("Erro: Arquivo 'dados_enchente.csv' não encontrado.")
    print("Por favor, execute o script 'gerar_dados.py' primeiro.")
    exit()

# Definir features (X) e o alvo (y)
features = ['prob_chuva', 'vento_kmh', 'nivel_rio_mm']
target = 'risco_enchente'

X = df[features]
y = df[target]

# Dividir os dados em conjuntos de treino e teste (prática padrão em ML)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

print(f"Dados divididos: {len(X_train)} para treino, {len(X_test)} para teste.")


# RandomForest
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')

print("Treinando o modelo RandomForestClassifier...")
model.fit(X_train, y_train)
print("Treinamento concluído.")

# Avaliar o modelo no conjunto de teste
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("\n--- Avaliação do Modelo no Conjunto de Teste ---")
print(f"Acurácia: {accuracy:.2f}")
print("Relatório de Classificação:")
print(classification_report(y_test, y_pred))

# Salvar o modelo treinado em um arquivo .pkl
with open('modelo_enchente.pkl', 'wb') as file:
    pickle.dump(model, file)

print("\nModelo treinado e salvo com sucesso como 'modelo_enchente.pkl'!")