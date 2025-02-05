from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn  # Required for running the FastAPI app

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

# Numbers API URL
NUMBERS_API_URL = "http://numbersapi.com/"

# Function to check if a number is prime
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

# Function to calculate the sum of digits
def sum_of_digits(n: int) -> int:
    return sum(int(digit) for digit in str(abs(n)))

# Function to check if a number is perfect
def is_perfect(n: int) -> bool:
    if n < 1:
        return False
    return sum(i for i in range(1, n) if n % i == 0) == n

# Function to determine parity (even or odd)
def get_parity(n: int) -> str:
    return "even" if n % 2 == 0 else "odd"

# Function to check if a number is an Armstrong number
def is_armstrong(n: int) -> bool:
    digits = [int(d) for d in str(n)]
    power = len(digits)
    return sum(d ** power for d in digits) == n

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Number Classification API! Use /api/classify-number?number=371"
    }

@app.get("/api/classify-number")
async def get_number_fact(number: int = Query(..., description="Enter a valid integer")):
    """Fetches a fact about a given number from Numbers API and additional properties."""
    if number < 0:
        raise HTTPException(status_code=400, detail="Number must be non-negative")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{NUMBERS_API_URL}{number}")
            response.raise_for_status()
            fun_fact = response.text
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=500, detail="Failed to fetch number fact")

    return {
        "number": number,
        "is_prime": is_prime(number),
        "is_perfect": is_perfect(number),
        "properties": [
            get_parity(number),
            "prime" if is_prime(number) else "composite",
            "perfect" if is_perfect(number) else "imperfect",
            "armstrong" if is_armstrong(number) else "not armstrong"
        ],
        "digit_sum": sum_of_digits(number),
        "fun_fact": fun_fact
    }

@app.exception_handler(ValueError)
async def validation_exception_handler(request, exc):
    """Handles invalid input errors."""
    return {
        "number": "alphabet",
        "error": True
    }, 400

# Run FastAPI using Uvicorn (Required for GCP)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080)
