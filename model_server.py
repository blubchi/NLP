"""
FitScore — Model Server (Bridge Only)
=======================================
Server ini hanya jembatan:
  proxy.js → model_server.py → handler.py → model → balik ke proxy

Tidak ada logika perhitungan di sini.
Semua scoring dan analisis dikerjakan oleh handler.py + model NER.

Cara pakai:
  1. Jalankan: python model_server.py
  2. Jalankan: node proxy.js
  3. Buka mainfinal.html → klik Analisis Sekarang
"""

import sys
import os
from flask import Flask, request, jsonify

app = Flask(__name__)
MODEL_PATH = "C:/Users/USER/OneDrive/Desktop/NLP/NER-AI-resume"
sys.path.insert(0, os.path.abspath(MODEL_PATH))

os.chdir(os.path.abspath(MODEL_PATH))

from handler import predict

print("✅ Handler berhasil dimuat dari:", os.getcwd())


@app.route("/predict", methods=["POST"])
def handle_predict():
    data   = request.get_json(force=True)
    inputs = data.get("inputs", data)
    result = predict(inputs)
    return jsonify(result)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════╗")
    print("║   FitScore Model Server — AKTIF ✅     ║")
    print("╠════════════════════════════════════════╣")
    print("║  Port    : http://localhost:8000        ║")
    print("║  Endpoint: POST /predict               ║")
    print("╚════════════════════════════════════════╝\n")
    app.run(host="0.0.0.0", port=8000, debug=False)