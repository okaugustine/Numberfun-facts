#!/bin/bash

# Exit on error
set -e

# Variables
APP_DIR="/home/ubuntu/number-classifier"
SERVER_IP="18.175.45.20"  # Replace with your server's public IP
SERVICE_NAME="number-classifier"

# Function to run shell commands
run_command() {
    echo "Running: $1"
    if ! eval "$1"; then
        echo "Error: Command failed - $1" >&2
        exit 1
    fi
}

# Update system and install dependencies
echo "Updating system packages..."
run_command "sudo apt update && sudo apt upgrade -y"
run_command "sudo apt install -y python3 python3-pip python3-venv nginx git"

# Setup virtual environment
echo "Setting up virtual environment..."
sudo mkdir -p "$APP_DIR"
sudo chown -R ubuntu:ubuntu "$APP_DIR"
cd "$APP_DIR"
python3 -m venv venv
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install fastapi uvicorn gunicorn

# Create FastAPI app with improved validation
cat <<EOF > "$APP_DIR/main.py"
from fastapi import FastAPI, Query

app = FastAPI()

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def is_perfect(n: int) -> bool:
    return n == sum(i for i in range(1, n) if n % i == 0)

def is_armstrong(n: int) -> bool:
    digits = [int(d) for d in str(abs(n))]
    power = len(digits)
    return sum(d ** power for d in digits) == abs(n)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Number Classifier API! Use '/api/classify-number' with a number query parameter."}

@app.get("/api/classify-number")
async def classify_number(number: str = Query(..., description="Enter a valid number")):
    try:
        num = int(number)
    except ValueError:
        return {
            "number": number,  # Keep the invalid input in response
            "error": True,
            "message": "Invalid input, must be a valid integer"
        }

    properties = ["even" if num % 2 == 0 else "odd"]
    if is_armstrong(num):
        properties.insert(0, "armstrong")

    return {
        "number": num,
        "is_prime": is_prime(num),
        "is_perfect": is_perfect(num),
        "properties": properties,
        "digit_sum": sum(map(int, str(abs(num)))),
        "fun_fact": f"{num} is an Armstrong number!" if is_armstrong(num) else f"{num} is an interesting number!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
EOF

# Create Gunicorn systemd service
cat <<EOF | sudo tee /etc/systemd/system/$SERVICE_NAME.service
[Unit]
Description=FastAPI Number Classifier
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8080 main:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
run_command "sudo systemctl daemon-reload"
run_command "sudo systemctl enable $SERVICE_NAME"
run_command "sudo systemctl restart $SERVICE_NAME"

# Configure NGINX
cat <<EOF | sudo tee /etc/nginx/sites-available/$SERVICE_NAME
server {
    listen 80;
    server_name $SERVER_IP;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

# Enable NGINX config
if [ ! -L /etc/nginx/sites-enabled/$SERVICE_NAME ]; then
    sudo ln -s /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/
fi
run_command "sudo systemctl restart nginx"

# Final status check
echo "Deployment complete!"
echo "Your API is live at: http://$SERVER_IP/api/classify-number?number=371"
run_command "sudo systemctl status $SERVICE_NAME --no-pager"
