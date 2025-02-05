Fun Fact Number Classifier API

🚀 Project Overview

This FastAPI-based web service classifies numbers based on their mathematical properties and provides an interesting fun fact about the number.

📌 Features

Classify a number as Prime, Perfect, Armstrong, Even, or Odd.

Calculate the sum of digits of the number.

Fetch a fun fact about the number from an external API.

Fast and efficient responses using ORJSON.

📂 Project Structure

NUMBERFUN-FACTS/
│-- main.py
│-- requirements.txt
│-- README.md

⚙️ Installation & Setup

1️⃣ Clone the Repository

git clone https://github.com/okaugustine/Numberfun-facts.git
cd funfact-project

2️⃣ Create a Virtual Environment (Optional but recommended)

python3 -m venv env
source env/bin/activate  # Mac/Linux
env\Scripts\activate  # Windows

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Run the FastAPI Server

uvicorn main:app --reload

The server will start on http://127.0.0.1:8000.

📌 API Endpoints

Method

Endpoint

Description

GET

/api/classify-number?number=50

Classifies a number and returns its properties and fun fact

Example Request

curl -X 'GET' 'http://127.0.0.1:8000/api/classify-number?number=50' -H 'accept: application/json'

Example Response

{
    "number": 50,
    "is_prime": false,
    "is_perfect": false,
    "properties": ["Even"],
    "digit_sum": 5,
    "fun_fact": "50 is the approximate number of times a mother hen turns her egg in a day so the yolk does not stick to the shell."
}

🛠️ Technologies Used

Python (FastAPI, ORJSON, Pydantic, Requests)

Uvicorn (ASGI Server)

📜 License

This project is licensed under the MIT License.

🙌 Contribution

Feel free to fork, modify, and submit a PR. Feedback and contributions are welcome! 🎉

📧 Contact

For any questions or suggestions, reach out to [ekenedilichukwuaugustine@gmail.com] or open an issue.