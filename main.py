from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import math

# Initialize FastAPI app
app = FastAPI()

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Numbers API Base URL
NUMBERS_API_URL = "http://numbersapi.com/"

def is_armstrong(n: int) -> bool:
    """Check if a number is an Armstrong number."""
    digits = [int(d) for d in str(abs(n))]  # Convert number to digits
    power = len(digits)
    return sum(d ** power for d in digits) == abs(n)

def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def is_perfect(n: int) -> bool:
    """Check if a number is a perfect number."""
    if n < 1:
        return False
    return sum(i for i in range(1, n) if n % i == 0) == n

def digit_sum(n: int) -> int:
    """Calculate the sum of a number's digits."""
    return sum(int(d) for d in str(abs(n)))

def get_parity(n: int) -> str:
    """Determine if the number is even or odd."""
    return "even" if n % 2 == 0 else "odd"

@app.get("/api/classify-number")
async def classify_number(number: str = Query(..., description="Enter a valid integer")):
    """Fetches a math fact about a given number and determines its properties."""

    # Validate if input is an integer
    if not number.lstrip("-").isdigit():
        return {"number": number, "error": True}  # ✅ Returns EXACTLY the required format

    number = int(number)  # Convert to integer after validation

    armstrong_status = is_armstrong(number)
    prime_status = is_prime(number)
    perfect_status = is_perfect(number)
    sum_of_digits = digit_sum(number)
    parity_status = get_parity(number)

    # Construct properties list
    properties = [parity_status]
    if armstrong_status:
        properties.insert(0, "armstrong")

    # Fetch fun fact from Numbers API (math type)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{NUMBERS_API_URL}{number}/math")
            response.raise_for_status()
            fun_fact = response.text.strip()
        except httpx.HTTPStatusError:
            fun_fact = "No math fact available."

    return {
        "number": number,
        "is_prime": prime_status,
        "is_perfect": perfect_status,
        "properties": properties,
        "digit_sum": sum_of_digits,
        "fun_fact": fun_fact
    }

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Number Classification API! Use /api/classify-number?number=371"
    }

# Run FastAPI using Uvicorn (Required for GCP)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)