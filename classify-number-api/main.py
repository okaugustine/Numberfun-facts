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

# Function to check if a number is Armstrong
def is_armstrong(num):
    digits = list(map(int, str(num)))
    power = len(digits)
    return num == sum(digit ** power for digit in digits)

# Function to calculate the sum of digits
def sum_of_digits(num):
    return sum(int(digit) for digit in str(num))

# Function to check if a number is prime
def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True

# Function to check if a number is perfect
def is_perfect(num):
    return sum(i for i in range(1, num) if num % i == 0) == num

# Route to classify the number and get the fun fact
@app.route('/api/classify-number', methods=['GET'])
def classify_number():
    number = flask.request.args.get('number')

    # Check if the input is a valid number
    try:
        number = int(number)
    except ValueError:
        return flask.jsonify({"number": number, "error": True, "message": "Invalid input"}), 400
    
    # Determine properties of the number
    properties = []
    if is_armstrong(number):
        properties.append("armstrong")
    properties.append("odd" if number % 2 != 0 else "even")

    # Calculate the sum of digits
    digit_sum = sum_of_digits(number)

    # Get a fun fact from Numbers API
    fun_fact = "No fun fact available"
    try:
        response = requests.get(f"http://numbersapi.com/{number}/math?json=true")
        if response.status_code == 200:
            fun_fact = response.json().get('text', 'No fun fact available')
    except:
        pass

    # Return the response in JSON format
    return flask.jsonify({
        "number": number,
        "is_prime": is_prime(number),
        "is_perfect": is_perfect(number),
        "properties": properties,
        "digit_sum": digit_sum,
        "fun_fact": fun_fact
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
