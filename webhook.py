from flask import Flask, request, jsonify, abort
import json
import datetime
import os

app = Flask(__name__)

TRAKTEER_TOKEN = "thrhook-PI7NasEROPBr2XIkKXQwAqXd"  # Ganti dengan token kamu

@app.route('/')
def index():
    return "Webhook Trakteer Aktif. Gunakan endpoint POST /trakteer_webhook"

@app.route('/trakteer_webhook', methods=['POST'])
def trakteer():
    token = request.headers.get("X-Webhook-Token")
    if token != TRAKTEER_TOKEN:
        return jsonify({"status": "error", "message": "Token tidak valid"}), 403

    data = request.get_json(force=True)
    note = data.get("note", "").strip()

    if not note.startswith("@"):
        return jsonify({"status": "error", "message": "Note tidak valid. Harus diawali @username"}), 400

    username = note[1:]
    amount = float(data.get("amount", 0))

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

    if not os.path.exists("database.json"):
        return jsonify({"status": "error", "message": "Database tidak ditemukan"}), 500

    with open("database.json", "r") as f:
        db = json.load(f)

    for uid, user in db.items():
        if user.get("username") == username:
            if days == "permanent":
                db[uid]["expired"] = "permanent"
            else:
                db[uid]["expired"] = (datetime.datetime.now() + datetime.timedelta(days=days)).isoformat()

            with open("database.json", "w") as f2:
                json.dump(db, f2, indent=2)

            return jsonify({"status": "success", "message": f"Berhasil update langganan {username}"}), 200

    return jsonify({"status": "error", "message": "Username tidak ditemukan"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"status": "error", "message": "Method tidak diizinkan"}), 405

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Agar cocok dengan Render
    app.run(host="0.0.0.0", port=port)
