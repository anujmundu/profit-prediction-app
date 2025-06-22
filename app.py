from flask import Flask, request, render_template
import joblib
import numpy as np
import pandas as pd


app = Flask(__name__)  # ✅ Define Flask application here

# Load the trained model and scaler
model = joblib.load("profit_prediction_model.pkl")
scaler = joblib.load("scaler.pkl")

@app.route("/", methods=["GET", "POST"])
def predict():
    profit = None
    summary = None
    if request.method == "POST":
        print("FILES:", request.files)
        try:
            # 🔹 1. Check for uploaded CSV first
            csv_file = request.files.get("csv_file")
            
            if csv_file and csv_file.filename.endswith(".csv"):
                df = pd.read_csv(csv_file)
                required_columns = ['R&D Spend', 'Administration', 'Marketing Spend']

                if not all(col in df.columns for col in required_columns):
                    return render_template("index.html", profit="❌ CSV missing required columns.")

                input_data = df[required_columns].values
                input_scaled = scaler.transform(input_data)
                predictions = model.predict(input_scaled)
                df['Predicted Profit'] = predictions

                df.to_csv("static/predictions.csv", index=False)
                return render_template("index.html", profit="✅ Predictions complete! <a href='static/predictions.csv' download>Download CSV</a>")

            # 🔹 2. Only handle manual input if no CSV file is submitted
            rnd_spend = request.form.get("rnd_spend", "").strip()
            admin_cost = request.form.get("admin_cost", "").strip()
            marketing_spend = request.form.get("marketing_spend", "").strip()

            if not rnd_spend or not admin_cost or not marketing_spend:
                return render_template("index.html", profit="⚠️ Error: Please enter all values.")

            # convert & predict
            input_data = np.array([[float(rnd_spend), float(admin_cost), float(marketing_spend)]])
            input_scaled = scaler.transform(input_data)
            prediction = model.predict(input_scaled)[0]

            if prediction < 0:
                profit = f"🔴 Predicted Loss: ₹{round(abs(prediction), 2)}"
                summary = (
                    f"The input values suggest a potential loss of ₹{round(abs(prediction), 2)}. "
                    "Consider reviewing expenses or adjusting the spending mix."
                )
            elif prediction < 100:
                profit = f"🟡 Predicted Profit: ₹{round(prediction, 2)}"
                summary = (
                    f"Expecting a modest profit of ₹{round(prediction, 2)}. Increasing marketing or R&D might help scale results."
                )
            else:
                profit = f"🟢 Predicted Profit: ₹{round(prediction, 2)}"
                summary = (
                    f"Great! You're on track to earn ₹{round(prediction, 2)} in profit — this combination seems effective."
                )

        except Exception as e:
            profit = f"❌ Something went wrong: {str(e)}"

    return render_template("index.html", profit=profit, summary=summary)


if __name__ == "__main__":
    print(">>> Starting Flask server...")
    app.run(debug=True)



