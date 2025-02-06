from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NUMBERS_API_URL = "http://numbersapi.com/"

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def sum_of_digits(n: int) -> int:
    return sum(int(digit) for digit in str(abs(n)))

def is_perfect(n: int) -> bool:
    if n < 1:
        return False
    return sum(i for i in range(1, n) if n % i == 0) == n

def is_armstrong(n: int) -> bool:
    digits = [int(d) for d in str(abs(n))]
    power = len(digits)
    return sum(d ** power for d in digits) == abs(n)

def get_parity(n: int) -> str:
    return "even" if n % 2 == 0 else "odd"

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Number Classification API! Use /api/classify-number?number=371"
    }

@app.get("/api/classify-number")
async def get_number_fact(number: str = Query(..., description="Enter a valid integer")):
    # **FIXED: Enhanced input validation**
    if not number.lstrip("-").isdigit():  # Ensures only integers are accepted
        return HTTPException(
            status_code=400,
            detail={
                "number": number,
                "error": True,
                "message": "Invalid number format. Please provide a valid integer.",
            }
        )

    number = int(number)  # Convert the valid string to an integer

    # Determine properties
    properties = []
    if is_armstrong(number):
        properties.append("armstrong")
    properties.append(get_parity(number))

    # Fetch fun fact
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{NUMBERS_API_URL}{number}/math")
            response.raise_for_status()
            fun_fact = response.text
        except httpx.HTTPStatusError:
            fun_fact = "No fact available"

    return {
        "number": number,
        "is_prime": is_prime(number),
        "is_perfect": is_perfect(number),
        "properties": properties,
        "digit_sum": sum_of_digits(number),
        "fun_fact": fun_fact
    }

# **Global Exception Handler for FastAPI Validation Errors**
@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    return HTTPException(
        status_code=400,
        detail={"error": True, "message": "Invalid input. Please provide a valid number."}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
