from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError
from datetime import datetime
import os

# === Configurazione ===
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://bet365odds:Aurora86@cluster0.svytet0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
DB_NAME = "bet365"

app = Flask(__name__)
CORS(app)  # abilita richieste da qualsiasi origine

# === Connessione a MongoDB ===
try:
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    db = client[DB_NAME]
    print("✅ Connessione a MongoDB riuscita")
except PyMongoError as e:
    print(f"❌ Errore connessione MongoDB: {e}")
    db = None


# === API principale ===
@app.route("/api/events")
def get_events():
    if db is None:
        return jsonify({"error": "MongoDB non connesso"}), 500

    sport = request.args.get("sport", "calcio")
    try:
        limit = int(request.args.get("limit", 200))
    except ValueError:
        limit = 200

    if sport not in db.list_collection_names():
        return jsonify({"error": f"Collezione '{sport}' non trovata"}), 404

    try:
        col = db[sport]
        eventi = list(col.find().limit(limit))

        def serialize(ev):
            new_ev = {}
            for k, v in ev.items():
                if isinstance(v, datetime):
                    new_ev[k] = v.isoformat()
                elif k == "_id":
                    new_ev[k] = str(v)
                else:
                    new_ev[k] = v
            return new_ev

        eventi_serializzati = [serialize(ev) for ev in eventi]
        return jsonify({"results": eventi_serializzati})

    except PyMongoError as e:
        return jsonify({"error": f"MongoDB error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/")
def home():
    return jsonify({"message": "✅ Server Flask attivo!"})


# === Avvio del server ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
