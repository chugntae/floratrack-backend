import tensorflow as tf
import numpy as np
from PIL import Image
import json
import os

# 📁 Caminhos seguros para os arquivos
base_dir = os.path.dirname(os.path.abspath(__file__))
modelo_path = os.path.join(base_dir, "modelo_flora_track.h5")
json_path = os.path.join(base_dir, "class_indices.json")

# 🔁 Carrega o modelo treinado
print("📦 Carregando modelo...")
model = tf.keras.models.load_model(modelo_path)
print("✅ Modelo carregado com sucesso!")

# 📁 Carrega o mapeamento de classes
if not os.path.exists(json_path):
    raise FileNotFoundError(f"Arquivo class_indices.json não encontrado em: {json_path}")

with open(json_path, "r") as f:
    class_indices = json.load(f)

# 🔄 Mapeia índice → nome da espécie
classe_para_nome = {v: k for k, v in class_indices.items()}

def preprocess_image(file_path):
    """Converte imagem para o formato que o modelo espera"""
    print(f"📸 Pré-processando imagem: {file_path}")
    image = Image.open(file_path).convert("RGB")
    image = image.resize((224, 224))
    image_array = np.array(image) / 255.0
    return np.expand_dims(image_array, axis=0)

def prever_especie(file_path):
    """Recebe caminho da imagem, retorna espécie e confiança"""
    imagem_preprocessada = preprocess_image(file_path)
    predicao = model.predict(imagem_preprocessada)[0]
    indice = int(np.argmax(predicao))
    especie = classe_para_nome.get(indice, "Desconhecida")
    confianca = float(predicao[indice])

    print(f"🔍 Índice previsto: {indice}")
    print(f"🔍 Espécie: {especie}")
    print(f"🔍 Confiança: {confianca:.2%}")

    return especie, confianca