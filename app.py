from utils import load_model
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    model = load_model()
    return "ExoHabitAI backend running 🚀"

@app.route("/health")
def health():
    model = load_model()
    return jsonify({"status": "ok"})
@app.route('/predict', methods=['GET','POST'])
def predict():
    try:
        if request.method == "GET":
            return "Send POST request with JSON data"

        model = load_model()

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

        return {
            "score": round(score,2),
            "status": "Habitable" if prediction==1 else "Not Habitable"
        }

    except Exception as e:
        return {"error": str(e)}

