from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import os
import sys

# 🔧 Garante que o Flask encontre o módulo 'modelo.py'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modelo import prever_especie  # Função de predição

app = Flask(__name__)
CORS(app)

# 🔧 Configuração do Cloudinary com variáveis de ambiente
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

@app.route('/prever', methods=['POST'])
def prever():
    imagem = request.files.get('imagem')

    if not imagem or not imagem.mimetype.startswith('image/'):
        print("⚠️ Arquivo inválido ou ausente")
        return jsonify({'erro': 'Imagem não recebida ou inválida'}), 400

    try:
        print(f"📥 Recebido arquivo: {imagem.filename}")

        # 🔧 Salva a imagem temporariamente
        temp_path = "temp.jpg"
        imagem.save(temp_path)

        # 🔍 Chamada ao modelo de ML
        especie_predita, confianca = prever_especie(temp_path)

        # 📤 Upload da imagem para Cloudinary
        resultado_upload = cloudinary.uploader.upload(
            temp_path,
            folder=f"floraTrack/{especie_predita}"
        )
        url_imagem = resultado_upload.get('secure_url')

        print(f"✅ Imagem enviada para Cloudinary: {url_imagem}")
        print(f"🧠 Espécie predita: {especie_predita} com confiança {confianca:.2%}")

        # 🧹 Remove o arquivo temporário
        os.remove(temp_path)

        return jsonify({
            'especie': especie_predita,
            'confianca': confianca,
            'imagemUrl': url_imagem
        })

    except Exception as e:
        print(f"❌ Erro no upload ou predição: {e}")
        return jsonify({'erro': 'Falha ao processar imagem'}), 500

# 🔧 Inicia o servidor Flask apenas localmente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
