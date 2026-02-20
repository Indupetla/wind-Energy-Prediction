import numpy as np
from flask import Flask, request, jsonify, render_template
import joblib
import requests

app = Flask(__name__)
model = joblib.load('power_prediction.sav')


@app.route('/')
def home():
    return render_template('intro.html')


@app.route('/predict')
def predict():
    return render_template('predict.html')


@app.route('/windapi', methods=['POST'])
def windapi():
    city = request.form.get('city')
    if not city:
        return render_template('predict.html', error="Please enter a city name.")

    apikey = "3b4a90e16b0cb4e1f747b974cfbcb2af"
    url = "http://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=" + apikey

    try:
        resp = requests.get(url, timeout=10)
        resp_json = resp.json()

        if resp.status_code != 200:
            error_msg = resp_json.get("message", "Could not fetch weather data.")
            return render_template('predict.html', error=f"API Error: {error_msg}")

        # Convert temperature from Kelvin to Celsius
        temp_kelvin = resp_json["main"]["temp"]
        temp_celsius = round(temp_kelvin - 273.15, 2)

        temp = str(temp_celsius) + " °C"
        humid = str(resp_json["main"]["humidity"]) + " %"
        pressure = str(resp_json["main"]["pressure"]) + " mmHG"
        speed = str(resp_json["wind"]["speed"]) + " m/s"

        return render_template('predict.html', temp=temp, humid=humid, pressure=pressure, speed=speed, city=city)

    except requests.exceptions.RequestException as e:
        return render_template('predict.html', error=f"Network error: Could not reach weather service. Please try again.")
    except (KeyError, TypeError) as e:
        return render_template('predict.html', error=f"Error parsing weather data for '{city}'. Please check the city name.")


@app.route('/y_predict', methods=['POST'])
def y_predict():
    try:
        theoretical_power = float(request.form.get('theoretical_power', 0))
        wind_speed = float(request.form.get('wind_speed', 0))

        x_test = [[theoretical_power, wind_speed]]
        prediction = model.predict(x_test)
        output = prediction[0]

        return render_template('predict.html',
                               prediction_text='The energy predicted is {:.2f} KWh'.format(output),
                               theoretical_power=theoretical_power,
                               wind_speed=wind_speed)
    except ValueError:
        return render_template('predict.html', error="Please enter valid numerical values for prediction.")
    except Exception as e:
        return render_template('predict.html', error=f"Prediction error: {str(e)}")


if __name__ == "__main__":
    app.run(debug=True)