from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
from datetime import datetime

# --- Configurazione Flask ---
app = Flask(__name__)
CORS(app)  # consente chiamate cross-origin

# --- Configurazione MongoDB Atlas ---
MONGO_URI = "mongodb+srv://bet365odds:Aurora86@cluster0.svytet0.mongodb.net/bet365?retryWrites=true&w=majority&tls=true"
DB_NAME = "bet365"

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print("✅ Connessione a MongoDB riuscita")
except PyMongoError as e:
    print(f"❌ Errore connessione MongoDB: {e}")
    db = None

# --- Route principale ---
@app.route("/")
def home():
    return jsonify({"message": "✅ Server Flask attivo!"})

# --- Endpoint per eventi ---
@app.route("/api/events")
def events():
    if db is None:
        return jsonify({"error": "MongoDB non connesso"}), 500

    sport = request.args.get("sport", "calcio")
    limit = int(request.args.get("limit", 200))

    if sport not in db.list_collection_names():
        return jsonify({"error": f"Collezione '{sport}' non trovata"}), 404

    try:
        col = db[sport]
        eventi = list(col.find().limit(limit))

        # Serializzazione sicura per ObjectId e datetime
        def serialize(ev):
            new_ev = {}
            for k, v in ev.items():
                if isinstance(v, datetime):
                    new_ev[k] = v.isoformat()
                elif isinstance(v, ObjectId):
                    new_ev[k] = str(v)
                else:
                    new_ev[k] = v
            return new_ev

        eventi_serializzati = [serialize(ev) for ev in eventi]
        return jsonify({"results": eventi_serializzati})
    except Exception as e:
        print("Errore:", e)
        return jsonify({"error": str(e)}), 500

# --- Avvio server su Render ---
if __name__ == "__main__":
    # Render richiede host 0.0.0.0 e porta specifica dall'ambiente
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
