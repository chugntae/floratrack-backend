from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import os
import sys
import traceback
import time
from dotenv import load_dotenv

# 🔧 Carrega variáveis de ambiente do .env
load_dotenv()

# 🔧 Garante que o Flask encontre o módulo 'modelo.py'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modelo import prever_especie  # Função de predição

app = Flask(__name__)
CORS(app)

# 🔧 Configuração do Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', 'FALHA'),
    api_key=os.getenv('CLOUDINARY_API_KEY', 'FALHA'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET', 'FALHA')
)

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        'cloud_name': cloudinary.config().cloud_name,
        'api_key': cloudinary.config().api_key,
        'api_secret': cloudinary.config().api_secret,
        'status': 'ok'
    })

@app.route('/prever', methods=['POST'])
def prever():
    inicio = time.time()
    imagem = request.files.get('imagem')

    if not imagem or not imagem.mimetype.startswith('image/'):
        print("⚠️ Arquivo inválido ou ausente")
        return jsonify({'erro': 'Imagem não recebida ou inválida'}), 400

    try:
        print(f"📥 Recebido arquivo: {imagem.filename}")
        temp_path = "temp.jpg"
        imagem.save(temp_path)
        print(f"📸 Imagem salva em disco ({time.time() - inicio:.2f}s)")

        print("🧠 Chamando modelo...")
        especie_predita, confianca = prever_especie(temp_path)
        print(f"✅ Modelo respondeu: {especie_predita} ({confianca:.2%}) em {time.time() - inicio:.2f}s")

        if not especie_predita or not isinstance(confianca, (float, int)):
            print("⚠️ Modelo retornou valores inválidos")
            os.remove(temp_path)
            return jsonify({'erro': 'Falha na predição'}), 500

        print("☁️ Enviando imagem para Cloudinary...")
        resultado_upload = cloudinary.uploader.upload(
            temp_path,
            folder=f"floraTrack/{especie_predita}",
            timeout=30
        )
        url_imagem = resultado_upload.get('secure_url')
        print(f"✅ Imagem enviada para Cloudinary: {url_imagem}")

        os.remove(temp_path)
        print(f"🧹 Arquivo temporário removido ({time.time() - inicio:.2f}s)")
        print(f"🏁 Tempo total de execução: {time.time() - inicio:.2f}s")

        return jsonify({
            'especie': especie_predita,
            'confianca': confianca,
            'imagemUrl': url_imagem
        })

    except Exception as e:
        traceback.print_exc()
        print(f"❌ Erro no upload ou predição: {e}")
        if os.path.exists("temp.jpg"):
            os.remove("temp.jpg")
        return jsonify({'erro': 'Falha ao processar imagem'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
