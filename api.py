import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from assets_data_prep import prepare_data

app = Flask(__name__)

# טוענים את המודל פעם אחת בעת הפעלת השרת
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trained_model.pkl")
model = joblib.load(MODEL_PATH)


@app.route("/")
def index():
    # מחזיר את דף ה-HTML הראשי
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(base_dir, "index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # בדיקה: האם יש נתונים בכלל
        if not data:
            return jsonify({"error": "לא התקבלו נתונים"}), 400

        # בדיקה: שדות חובה חייבים להיות קיימים
        required_fields = ["genres", "startYear", "runtimeMinutes", "primaryTitle"]
        for field in required_fields:
            if field not in data or str(data[field]).strip() == "":
                return jsonify({"error": f"שדה חסר או ריק: {field}"}), 400

        # בדיקה: startYear ו-runtimeMinutes חייבים להיות מספרים
        try:
            start_year = float(data["startYear"])
            runtime = float(data["runtimeMinutes"])
        except (ValueError, TypeError):
            return jsonify({"error": "startYear ו-runtimeMinutes חייבים להיות מספרים"}), 400

        # בדיקה: טווחים תואמים לנתוני האימון (חלק 1)
        if not (1900 <= start_year <= 2024):
            return jsonify({"error": "startYear חייב להיות בין 1900 ל-2024"}), 400
        if not (60 <= runtime <= 300):
            return jsonify({"error": "runtimeMinutes חייב להיות בין 60 ל-300 (לפי פילטר נתוני האימון)"}), 400

        # בניית שורה אחת עם כל השדות שprepare_data מצפה להם
        row = {
            "genres":         data.get("genres", ""),
            "startYear":      start_year,
            "runtimeMinutes": runtime,
            "lead_actors_ids": data.get("lead_actors_ids", ""),
            "primaryTitle":   data.get("primaryTitle", ""),
            "Language":       data.get("Language", ""),
            "Country":        data.get("Country", ""),
            "budget":         float(data["budget"]) if data.get("budget") else None,
        }

        # מריצים prepare_data ואז predict
        df_input = pd.DataFrame([row])
        X = prepare_data(df_input)
        prediction = model.predict(X)[0]

        # מגבילים לטווח 1-10 ומעגלים לספרה אחת
        prediction = round(float(prediction), 1)
        prediction = max(1.0, min(10.0, prediction))

        return jsonify({"predicted_rating": prediction})

    except Exception as e:
        return jsonify({"error": f"שגיאה פנימית: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
