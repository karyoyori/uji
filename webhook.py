from flask import Flask, request, jsonify
import json
import datetime
import os

app = Flask(__name__)

TRAKTEER_TOKEN = "thrhook-PI7NasEROPBr2XIkKXQwAqXd"  # Ganti dengan tokenmu

DATABASE_FILE = "database.json"

def load_database():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "w") as f:
            json.dump({}, f)
    with open(DATABASE_FILE, "r") as f:
        return json.load(f)

def save_database(db):
    with open(DATABASE_FILE, "w") as f:
        json.dump(db, f, indent=2)

@app.route('/')
def index():
    return "Webhook Trakteer Aktif! Gunakan endpoint POST /trakteer_webhook"

@app.route('/trakteer_webhook', methods=['POST'])
def trakteer_webhook():
    token = request.headers.get("X-Webhook-Token")
    if token != TRAKTEER_TOKEN:
        return jsonify({"status": "error", "message": "Token tidak valid"}), 403

    data = request.get_json(force=True)
    note = data.get("note", "").strip()

    if not note.startswith("@"):
        return jsonify({"status": "error", "message": "Note tidak valid. Harus diawali dengan @IDTelegram"}), 400

    user_id = note[1:]  # hapus tanda '@'
    amount = float(data.get("amount", 0))

    # Hitung durasi berdasarkan amount
    if amount == 1000:
        days = 1
    elif amount == 5000:
        days = 3
    elif amount == 10000:
        days = 6
    elif amount == 30000:
        days = 30
    elif amount == 100000:
        days = "permanent"
    else:
        return jsonify({"status": "error", "message": "Nominal tidak dikenali"}), 400

    db = load_database()

    now = datetime.datetime.now()
    
    if user_id not in db:
        # Kalau user belum ada, buat baru
        db[user_id] = {
            "expired": None  # Nanti diisi di bawah
        }

    if days == "permanent":
        db[user_id]["expired"] = "permanent"
    else:
        # Hitung expired baru
        db[user_id]["expired"] = (now + datetime.timedelta(days=days)).isoformat()

    save_database(db)

    return jsonify({"status": "success", "message": f"VIP untuk ID {user_id} berhasil diperpanjang!"}), 200

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"status": "error", "message": "Method tidak diizinkan"}), 405

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Agar cocok di Render.com
    app.run(host="0.0.0.0", port=port)
