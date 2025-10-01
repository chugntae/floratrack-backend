import numpy as np
from PIL import Image
import tensorflow as tf
import json
import os

# 📁 Caminhos seguros
base_dir = os.path.dirname(os.path.abspath(__file__))
modelo_path = os.path.join(base_dir, "modelo_flora_track.tflite")
json_path = os.path.join(base_dir, "class_indices.json")

# 🔁 Carrega o modelo TFLite
print("📦 Carregando modelo TFLite...")
interpreter = tf.lite.Interpreter(model_path=modelo_path)
interpreter.allocate_tensors()
print("✅ Modelo TFLite carregado!")

# 🔍 Detalhes dos tensores
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# 📁 Carrega o mapeamento de classes
if not os.path.exists(json_path):
    raise FileNotFoundError(f"Arquivo class_indices.json não encontrado em: {json_path}")

with open(json_path, "r") as f:
    class_indices = json.load(f)

classe_para_nome = {v: k for k, v in class_indices.items()}

def preprocess_image(file_path):
    try:
        print(f"📸 Pré-processando imagem: {file_path}")
        image = Image.open(file_path).convert("RGB")
        image = image.resize((224, 224))
        image_array = np.array(image, dtype=np.float32) / 255.0
        return np.expand_dims(image_array, axis=0)
    except Exception as e:
        print(f"❌ Erro ao pré-processar imagem: {e}")
        return None

def prever_especie(file_path, limiar_confianca=0.5):
    imagem_preprocessada = preprocess_image(file_path)
    if imagem_preprocessada is None:
        return "Desconhecida", 0.0

    try:
        print("🧠 Rodando predição com TFLite...")
        interpreter.set_tensor(input_details[0]['index'], imagem_preprocessada)
        interpreter.invoke()
        predicao = interpreter.get_tensor(output_details[0]['index'])[0]

        indice = int(np.argmax(predicao))
        especie = classe_para_nome.get(indice, "Desconhecida")
        confianca = float(predicao[indice])

        print(f"🔍 Índice previsto: {indice}")
        print(f"🔍 Espécie: {especie}")
        print(f"🔍 Confiança: {confianca:.2%}")

        if confianca >= limiar_confianca:
            return especie, confianca
        else:
            print(f"⚠️ Confiança abaixo do limiar ({limiar_confianca:.2%})")
            return "Desconhecida", confianca

    except Exception as e:
        print(f"❌ Erro na predição TFLite: {e}")
        return "Desconhecida", 0.0
