#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "[*] Installing system dependencies..."
sudo apt update -y
sudo apt install -y python3 python3-venv python3-pip curl nmap sqlmap sqlite3

echo "[*] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "[*] Adding vshop.in to /etc/hosts..."
grep -q "vshop.in" /etc/hosts || echo "127.0.0.1  vshop.in www.vshop.in" | sudo tee -a /etc/hosts

echo "[*] Creating directories..."
mkdir -p app/static/css app/static/images app/static/uploads app/templates scripts docs
touch app/__init__.py
chmod 777 app/static/uploads

echo "[*] Initializing database..."
python3 app/init_db.py

echo "[*] Fetching product images..."
chmod +x scripts/fetch_images.sh && ./scripts/fetch_images.sh

echo ""
echo "[+] SETUP COMPLETE"
echo "[+] Start the app:  ./run.sh"
echo "[+] Browse:         http://vshop.in:5000"
echo "[+] Admin panel:    http://vshop.in:5000/admin  (admin / admin123)"
