from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
import os

# Caminho para o modelo treinado
modelo_path = "modelo_flora_track.h5"
model = load_model(modelo_path, compile=False)  # Evita erro de métricas personalizadas

# Lista de classes (nomes das espécies)
classes = sorted(os.listdir("dataset_split/train"))

def prever_especie(img_path):
    try:
        # Carrega e pré-processa a imagem
        img = load_img(img_path, target_size=(224, 224))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0  # Normalização

        # Faz a previsão
        pred = model.predict(img_array)
        indice = np.argmax(pred)
        confianca = float(np.max(pred)) * 100

        especie_prevista = classes[indice]
        return {
            "especie": especie_prevista,
            "confianca": round(confianca, 2)
        }

    except Exception as e:
        return {
            "erro": str(e)
        }

# Testes locais
if __name__ == "__main__":
    resultado1 = prever_especie("C:\\Users\\taeya\\Downloads\\flora_track_backend\\imagens_especies\\piteira-do-caribe\\20250911_110729.jpg")
    print(f"🌱 Espécie prevista (piteira-do-caribe): {resultado1['especie']} ({resultado1['confianca']}% de confiança)")

    resultado2 = prever_especie("C:\\Users\\taeya\\Downloads\\flora_track_backend\\imagens_especies\\onze-horas\\IMG_3908.JPG")
    print(f"🌱 Espécie prevista (onze-horas): {resultado2['especie']} ({resultado2['confianca']}% de confiança)")