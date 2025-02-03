import flask
import requests
from flask_cors import CORS
from flask import jsonify

app = flask.Flask(__name__)
CORS(app)  # Allow Cross-Origin Resource Sharing

# Home route to check if the app is running correctly
@app.route('/')
def hello():
    return "Hello, World!"

# Function to check if a number is an Armstrong number
def is_armstrong(num):
    digits = [int(digit) for digit in str(num)]
    power = len(digits)
    return num == sum(digit ** power for digit in digits)

# Function to calculate the sum of digits
def sum_of_digits(num):
    return sum(int(digit) for digit in str(num))

# Function to check if a number is perfect
def is_perfect(num):
    divisors = [i for i in range(1, num) if num % i == 0]
    return sum(divisors) == num

# Function to check if a number is prime
def is_prime(num):
    if num < 2:
        return False
    return all(num % i != 0 for i in range(2, int(num ** 0.5) + 1))

@app.route('/api/classify-number', methods=['GET'])
def classify_number():
    number = flask.request.args.get('number')

    # Validate input
    try:
        number = int(number)
    except ValueError:
        return flask.jsonify({"error": "Invalid number format"}), 400

    # Classify properties
    properties = []
    if is_armstrong(number):
        properties.append("armstrong")
    if number % 2 == 0:
        properties.append("even")
    else:
        properties.append("odd")
    if is_perfect(number):
        properties.append("perfect")

    # Fetch fun fact from Numbers API
    try:
        response = requests.get(f"http://numbersapi.com/{number}/math?json=true")
        response.raise_for_status()
        fun_fact = response.json().get("text", "No fun fact available")
    except requests.RequestException:
        fun_fact = "Could not retrieve fun fact."

    # Construct JSON response
    response_data = {
        "number": number,
        "is_prime": is_prime(number),
        "is_perfect": is_perfect(number),
        "properties": properties,
        "digit_sum": sum_of_digits(number),
        "fun_fact": fun_fact
    }

    return flask.jsonify(response_data), 200

if __name__ == '__main__':
    from os import environ
    port = int(environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
