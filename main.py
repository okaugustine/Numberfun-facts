import os
import subprocess

def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        exit(1)
    print(result.stdout)

APP_DIR = "/home/ubuntu/number-classifier"
SERVICE_NAME = "number-classifier"
SERVER_IP = "18.175.45.20"  # Replace with your server IP

# Update system and install dependencies
run_command("sudo apt update && sudo apt upgrade -y")
run_command("sudo apt install -y python3 python3-pip python3-venv nginx git")

# Setup virtual environment
os.makedirs(APP_DIR, exist_ok=True)
run_command(f"sudo chown -R $(whoami):$(whoami) {APP_DIR}")
os.chdir(APP_DIR)
run_command("python3 -m venv venv")
run_command(f"{APP_DIR}/venv/bin/pip install --upgrade pip")
run_command(f"{APP_DIR}/venv/bin/pip install fastapi uvicorn gunicorn httpx")

# Create FastAPI application
fastapi_app = f"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {{
        "message": "Welcome to the Number Classification API! Use /api/classify-number?number=371"
    }}

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
    return sum(int(digit) for d in str(abs(n)))

def is_perfect(n: int) -> bool:
    if n < 1:
        return False
    return sum(i for i in range(1, n) if n % i == 0) == n

def get_parity(n: int) -> str:
    return "even" if n % 2 == 0 else "odd"

def is_armstrong(n: int) -> bool:
    digits = [int(d) for d in str(abs(n))]
    power = len(digits)
    return sum(d ** power for d in digits) == abs(n)

@app.get("/api/classify-number")
async def get_number_fact(number: float = Query(..., description="Enter a valid number")):
    num_int = int(number) if number.is_integer() else None

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{NUMBERS_API_URL}{number}")
            response.raise_for_status()
            fun_fact = response.text
        except httpx.HTTPStatusError:
            fun_fact = "No fact available"

    return {{
        "number": number,
        "is_prime": is_prime(num_int) if num_int is not None else None,
        "is_perfect": is_perfect(num_int) if num_int is not None else None,
        "properties": [
            get_parity(num_int) if num_int is not None else "N/A",
            "prime" if num_int is not None and is_prime(num_int) else "composite",
            "perfect" if num_int is not None and is_perfect(num_int) else "imperfect",
            "armstrong" if num_int is not None and is_armstrong(num_int) else "not armstrong"
        ],
        "digit_sum": sum_of_digits(num_int) if num_int is not None else "N/A",
        "fun_fact": fun_fact
    }}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
"""

with open(f"{APP_DIR}/main.py", "w") as f:
    f.write(fastapi_app)

# Create Gunicorn systemd service
systemd_service = f"""
[Unit]
Description=FastAPI Number Classifier
After=network.target

[Service]
User=$(whoami)
Group=$(whoami)
WorkingDirectory={APP_DIR}
Environment="PATH={APP_DIR}/venv/bin"
ExecStart={APP_DIR}/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8080 main:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
with open(f"/etc/systemd/system/{SERVICE_NAME}.service", "w") as f:
    f.write(systemd_service)

# Reload systemd and start service
run_command("sudo systemctl daemon-reload")
run_command(f"sudo systemctl enable {SERVICE_NAME}")
run_command(f"sudo systemctl restart {SERVICE_NAME}")

# Configure NGINX
nginx_config = f"""
server {{
    listen 80;
    server_name {SERVER_IP};

    location / {{
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }}
}}
"""
with open(f"/etc/nginx/sites-available/{SERVICE_NAME}", "w") as f:
    f.write(nginx_config)

# Enable NGINX config
if not os.path.exists(f"/etc/nginx/sites-enabled/{SERVICE_NAME}"):
    run_command(f"sudo ln -s /etc/nginx/sites-available/{SERVICE_NAME} /etc/nginx/sites-enabled/")
run_command("sudo systemctl restart nginx")

# Final status check
print("Deployment complete!")
print(f"Your API is live at: http://{SERVER_IP}/api/classify-number?number=371")
run_command(f"sudo systemctl status {SERVICE_NAME} --no-pager")
