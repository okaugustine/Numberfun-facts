from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import math
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Numbers API Base URL
NUMBERS_API_URL = "http://numbersapi.com/"

def is_armstrong(n: int) -> bool:
    digits = [int(d) for d in str(abs(n))]
    power = len(digits)
    return sum(d ** power for d in digits) == abs(n)

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def is_perfect(n: int) -> bool:
    if n < 1:
        return False
    return sum(i for i in range(1, n) if n % i == 0) == n

def digit_sum(n: int) -> int:
    return sum(int(d) for d in str(abs(n)))

def get_parity(n: int) -> str:
    return "even" if n % 2 == 0 else "odd"

@app.get("/api/classify-number")
async def classify_number(number: str = Query(..., description="Enter a valid integer")):
    # Validate input as integer
    if not number.lstrip("-").isdigit():
        raise HTTPException(status_code=400, detail="Invalid input: Must be an integer")
    
    number = int(number)
    response_data = {
        "number": number,
        "is_prime": is_prime(number),
        "is_perfect": is_perfect(number),
        "properties": ["armstrong"] if is_armstrong(number) else [],
        "digit_sum": digit_sum(number),
        "fun_fact": ""
    }
    response_data["properties"].append(get_parity(number))
    
    # Fetch fun fact from Numbers API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{NUMBERS_API_URL}{number}/math")
            response.raise_for_status()
            response_data["fun_fact"] = response.text.strip()
        except httpx.HTTPStatusError:
            response_data["fun_fact"] = "No math fact available."
    
    return response_data

@app.get("/")
def read_root():
    return {"message": "Welcome to the Number Classification API! Use /api/classify-number?number=371"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
