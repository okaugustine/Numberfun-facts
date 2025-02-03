import flask
import requests
import os
from flask_cors import CORS

app = flask.Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return flask.jsonify({
        "message": "Welcome to the Number Classifier API!",
        "usage": "/api/classify-number?number=<num>"
    }), 200

@app.route('/api/classify-number', methods=['GET'])
def classify_number():
    number = flask.request.args.get('number')

    try:
        number = int(number)
    except ValueError:
        return flask.jsonify({"number": number, "error": True, "message": "Invalid input"}), 400

    properties = ["odd" if number % 2 != 0 else "even"]
    if sum(int(digit) ** len(str(number)) for digit in str(number)) == number:
        properties.insert(0, "armstrong")

    digit_sum = sum(int(digit) for digit in str(number))

    fun_fact = "No fun fact available"
    try:
        response = requests.get(f"http://numbersapi.com/{number}/math?json=true")
        if response.status_code == 200:
            fun_fact = response.json().get('text', 'No fun fact available')
    except:
        pass

    return flask.jsonify({
        "number": number,
        "is_prime": number > 1 and all(number % i != 0 for i in range(2, int(number**0.5) + 1)),
        "is_perfect": False,
        "properties": properties,
        "digit_sum": digit_sum,
        "fun_fact": fun_fact
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
