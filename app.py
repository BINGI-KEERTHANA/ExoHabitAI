from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
import os
from utils import load_model

FEATURE_NAMES = [
    'pl_rade','pl_orbper','pl_orbsmax','pl_eqt','st_teff','st_rad',
    'st_mass','st_met','disc_year','default_flag','pl_bmasse',
    'pl_density','st_luminosity','pl_eqt_norm','pl_rade_norm',
    'pl_orbsmax_norm','st_luminosity_norm','st_teff_norm',
    'st_rad_norm','st_lum_norm','temp_star_score','size_star_score',
    'radiation_score','stellar_compatibility_index','pl_orbper_norm',
    'period_stability_score','distance_stability_score',
    'orbital_stability_factor'
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)

# ✅ simple test route
@app.route("/")
def home():
    return "ExoHabitAI backend running 🚀"

# ================= PREDICT =================
@app.route('/predict', methods=['POST'])
def predict():
    model = load_model()   # ✅ load here

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

# ================= RANK =================
@app.route("/rank", methods=["GET"])
def rank_planets():
    try:
        path = os.path.join(BASE_DIR,"data","processed","habitability_ranked.csv")

        if not os.path.exists(path):
            return jsonify({"error":"Ranking file not found"}),404

        df = pd.read_csv(path)

        if "habitability_probability" not in df.columns:
            return jsonify({"error":"Column missing"}),500

        top = df.sort_values("habitability_probability",ascending=False).head(10)

        return jsonify({
            "count":len(top),
            "top_habitable_planets":top.to_dict(orient="records")
        })

    except Exception as e:
        return jsonify({"error":str(e)}),500

# ================= IMPORTANCE =================
@app.route("/importance", methods=["GET"])
def importance():
    try:
        model = load_model()
        clf = model.named_steps["classifier"]

        return jsonify({
            "features": FEATURE_NAMES,
            "importance": abs(clf.coef_[0]).tolist()
        })

    except Exception as e:
        return jsonify({"error":str(e)}),500

# ================= UPLOAD =================
@app.route("/upload_rank", methods=["POST"])
def upload_rank():
    model = load_model()   # ✅ load here

    file = request.files["file"]
    df = pd.read_csv(file)

    probs = model.predict_proba(df[FEATURE_NAMES])[:,1]
    df["habitability_probability"] = probs
    df.sort_values("habitability_probability", ascending=False, inplace=True)

    save_path = os.path.join(BASE_DIR,"data","processed","uploaded_ranked.csv")
    df.to_csv(save_path, index=False)

    return jsonify({"status":"saved"})
