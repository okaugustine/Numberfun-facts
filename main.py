import flask
import requests
import os
from flask_cors import CORS

app = flask.Flask(__name__)
CORS(app)

# Function to check if a number is Armstrong
def is_armstrong(num):
    digits = list(map(int, str(num)))
    power = len(digits)
    return num == sum(digit ** power for digit in digits)

# Function to calculate the sum of digits
def sum_of_digits(num):
    return sum(int(digit) for digit in str(num))

# Route to serve the frontend page
@app.route('/')
def home():
    return flask.send_from_directory('.', 'index.html')

# Route to classify the number
@app.route('/api/classify-number', methods=['GET'])
def classify_number():
    number = flask.request.args.get('number')

    try:
        number = int(number)
    except ValueError:
        return flask.jsonify({"error": "Invalid number"}), 400
    
    is_prime = number > 1 and all(number % i != 0 for i in range(2, int(number**0.5) + 1))
    
    properties = []
    if is_armstrong(number):
        properties.append("Armstrong Number")
    properties.append("Odd" if number % 2 != 0 else "Even")
    
    digit_sum = sum_of_digits(number)
    
    response = requests.get(f"http://numbersapi.com/{number}/math?json=true")
    fun_fact = response.json().get('text', 'No fun fact available')

    # Format response with line breaks
    formatted_response = f"""
    Number: {number}
    Prime: {'Yes' if is_prime else 'No'}
    Properties: {', '.join(properties)}
    Sum of Digits: {digit_sum}
    Fun Fact: {fun_fact}
    """

    return flask.jsonify({"output": formatted_response.strip()})

# Run the application
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
