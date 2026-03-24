from flask import Flask, jsonify, request, send_file, render_template
import json
import os
from datetime import datetime
import pandas as pd
from threading import Lock
import tempfile

app = Flask(__name__)

DATA_FILE = "musteriler.json"
file_lock = Lock()

# -----------------------------
# Veri İşlemleri
# -----------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def next_id(data):
    # Silme sonrası ID çakışmasını önlemek için max+1
    return (max([m.get("id", 0) for m in data], default=0) + 1)

# -----------------------------
# Hesaplamalar
# -----------------------------
def hesapla_risk(musteri):
    gelir = float(musteri.get("gelir", 0) or 0)
    borc = float(musteri.get("borc", 0) or 0)
    gecikme = int(musteri.get("gecikme_gun", 0) or 0)

    oran = borc / gelir if gelir > 0 else 0

    if oran > 0.5:
        return "Riskli"
    elif gecikme > 30:
        return "Yüksek Risk"
    elif gecikme > 2:
        return "Orta Risk"
    else:
        return "Düşük Risk"

def gecikme_hesapla(odeme_tarihi):
    try:
        odeme = datetime.strptime(odeme_tarihi, "%Y-%m-%d")
        bugun = datetime.now()
        fark = (bugun - odeme).days
        return max(fark, 0)
    except Exception:
        return 0

def normalize_musteri_payload(payload):
    # Basit doğrulama/normalize
    ad = (payload.get("ad") or "").strip()
    telefon = (payload.get("telefon") or "").strip()
    tcno = (payload.get("tcno") or "").strip()  # TC Kimlik No
    odeme_tarihi = (payload.get("odeme_tarihi") or "").strip()

    if not ad:
        raise ValueError("ad zorunlu")
    if not odeme_tarihi:
        raise ValueError("odeme_tarihi zorunlu (YYYY-MM-DD)")
    # İstersen TC doğrulama regex ekle:
    # import re
    # if not re.match(r'^\d{11}$', tcno):
    #     raise ValueError("Geçerli 11 haneli TC Kimlik No girilmelidir")

    musteri = {
        "ad": ad,
        "telefon": telefon,
        "tcno": tcno,
        "gelir": float(payload.get("gelir", 0) or 0),
        "gider": float(payload.get("gider", 0) or 0),
        "borc": float(payload.get("borc", 0) or 0),
        "odeme_tarihi": odeme_tarihi,
    }
    musteri["gecikme_gun"] = gecikme_hesapla(musteri["odeme_tarihi"])
    musteri["risk"] = hesapla_risk(musteri)
    return musteri

# -----------------------------
# Sayfa
# -----------------------------
@app.get("/")
def index():
    return render_template("index.html")

# -----------------------------
# API - Müşteriler
# -----------------------------
@app.get("/api/customers")
def get_customers():
    data = load_data()
    data = sorted(data, key=lambda x: x.get("id", 0))
    return jsonify(data)

@app.post("/api/customers")
def create_customer():
    payload = request.get_json(force=True, silent=True) or {}
    try:
        musteri = normalize_musteri_payload(payload)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    with file_lock:
        data = load_data()
        musteri["id"] = next_id(data)
        data.append(musteri)
        save_data(data)

    return jsonify(musteri), 201

@app.put("/api/customers/<int:customer_id>")
def update_customer(customer_id: int):
    payload = request.get_json(force=True, silent=True) or {}
    try:
        updated = normalize_musteri_payload(payload)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    with file_lock:
        data = load_data()
        found = False
        for m in data:
            if m.get("id") == customer_id:
                updated["id"] = customer_id
                m.clear()
                m.update(updated)
                found = True
                break

        if not found:
            return jsonify({"error": "Müşteri bulunamadı"}), 404

        save_data(data)

    return jsonify(updated)

@app.delete("/api/customers/<int:customer_id>")
def delete_customer(customer_id: int):
    with file_lock:
        data = load_data()
        new_data = [m for m in data if m.get("id") != customer_id]
        if len(new_data) == len(data):
            return jsonify({"error": "Müşteri bulunamadı"}), 404
        save_data(new_data)

    return jsonify({"ok": True})

# -----------------------------
# API - Dashboard
# -----------------------------
@app.get("/api/dashboard")
def get_dashboard():
    data = load_data()

    toplam_musteri = len(data)
    riskli = len([m for m in data if m.get("risk") != "Düşük Risk"])
    toplam_borc = sum([float(m.get("borc", 0) or 0) for m in data])
    gecikmeli = len([m for m in data if int(m.get("gecikme_gun", 0) or 0) > 0])

    en_riskli = sorted(
        data,
        key=lambda x: int(x.get("gecikme_gun", 0) or 0),
        reverse=True
    )[:5]

    return jsonify({
        "toplam_musteri": toplam_musteri,
        "riskli": riskli,
        "toplam_borc": toplam_borc,
        "gecikmeli": gecikmeli,
        "en_riskli": en_riskli
    })

# -----------------------------
# Excel Export
# -----------------------------
@app.get("/api/export/excel")
def export_excel():
    data = load_data()
    df = pd.DataFrame(data)

    tmp_dir = tempfile.gettempdir()
    file_path = os.path.join(tmp_dir, "musteriler.xlsx")
    df.to_excel(file_path, index=False)

    return send_file(
        file_path,
        as_attachment=True,
        download_name="musteriler.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)