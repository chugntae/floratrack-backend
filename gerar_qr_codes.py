import firebase_admin
from firebase_admin import credentials, firestore
import qrcode
import os

# 🔐 Inicializa Firebase
cred = credentials.Certificate("scripts/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 📁 Garante que a pasta qr_codes existe
os.makedirs("qr_codes", exist_ok=True)

# 🔍 Acessa a subcoleção todasAsPlantas
subcolecao = db.collection("identificadores").document("plantasss").collection("todasAsPlantas")
docs = subcolecao.stream()

# 📷 Gera QR Code para cada planta
for doc in docs:
    data = doc.to_dict()
    id_planta = data.get("idPlanta")
    nome = data.get("nomePopular", "desconhecida")

    if id_planta:
        qr = qrcode.make(id_planta)
        qr.save(f"qr_codes/{id_planta}.png")
        print(f"✅ QR Code gerado para {nome} → {id_planta}")
    else:
        print(f"⚠️ Planta sem ID: {nome}")