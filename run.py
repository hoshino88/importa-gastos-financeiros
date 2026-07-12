import subprocess
import time
import os
import sys

# 1. Força a porta principal a ser a 8000 (onde o tráfego público do Railway vai chegar)
porta_publica_nuvem = os.getenv("PORT", "8000")

# 2. Fixa o FastAPI (Backend) numa porta interna alternativa
porta_interna_fastapi = "8080"

# Força o dashboard do Streamlit a apontar para a API local interna
os.environ["URL_API_BACKEND"] = f"http://127.0.0.1:{porta_interna_fastapi}"

print(f"🚀 A iniciar o Backend FastAPI na porta interna {porta_interna_fastapi}...")
backend_process = subprocess.Popen([
    sys.executable, "-m", "uvicorn", "src.importa_gastos.main:app",
    "--host", "127.0.0.1",
    "--port", porta_interna_fastapi
])

# Aguarda 3 segundos para o backend estabilizar
time.sleep(3)

print(f"🖥️ A iniciar o Streamlit Dashboard na porta pública {porta_publica_nuvem}...")
streamlit_process = subprocess.Popen([
    sys.executable, "-m", "streamlit", "run", "dashboard.py",
    "--server.port", porta_publica_nuvem,
    "--server.address", "0.0.0.0",
    "--server.headless", "true"
])

# Mantém o script vivo a monitorizar os dois processos
try:
    backend_process.wait()
    streamlit_process.wait()
except KeyboardInterrupt:
    backend_process.terminate()
    streamlit_process.terminate()