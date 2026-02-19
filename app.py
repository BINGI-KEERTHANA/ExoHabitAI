from utils import load_model
from flask import Flask, request, jsonify
from flask_cors import CORS   # ✅ ADD THIS

app = Flask(__name__)
CORS(app)   # ✅ ADD THIS

# LOAD MODEL ONCE AT STARTUP
model = load_model()

@app.route("/")
def home():
    return "ExoHabitAI backend running 🚀"

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route('/predict', methods=['GET','POST'])
def predict():
    try:
        if request.method == "GET":
            return "Send POST request with JSON data"

        data = request.get_json()

        radius = float(data['radius'])
        mass = float(data['mass'])
        temp = float(data['temperature'])
        distance = float(data['distance'])

        eqt = 288 * (temp/5778)**0.25 / (distance**0.5)
        density = mass / (radius**3 + 1e-6)
        period = 365 * (distance**1.5)

        features = [[
            radius, period, distance, eqt, temp,
            1.0,1.0,0.0,2020,1,
            mass, density,(temp/5778)**4,
            0.5,0.5,0.5,0.5,0.5,0.5,0.5,
            0.7,0.7,0.7,0.7,
            0.5,0.6,0.6,0.6
        ]]

        prediction = model.predict(features)[0]

        try:
            score = float(model.predict_proba(features)[0][1])
        except:
            score = float(prediction)

        return jsonify({
            "score": round(score,2),
            "status": "Habitable" if prediction==1 else "Not Habitable"
        })

    except Exception as e:
        return jsonify({"error": str(e)})
