import subprocess
import time
import os
import sys

# Deteta a porta que a Railway vai dar para a aplicação (padrão é a variável PORT)
porta_nuvem = os.getenv("PORT", "8501")

# 1. Força o dashboard a apontar para a API local interna (na porta 8000)
os.environ["URL_API_BACKEND"] = "http://127.0.0.1:8000"

print("🚀 A iniciar o Backend FastAPI na porta 8000...")
backend_process = subprocess.Popen([
    sys.executable, "-m", "uvicorn", "src.importa_gastos.main:app",
    "--host", "127.0.0.1",
    "--port", "8000"
])

# Aguarda 3 segundos para o backend estabilizar antes de abrir a interface
time.sleep(3)

print(f"🖥️ A iniciar o Streamlit Dashboard na porta {porta_nuvem}...")
# Inicia o streamlit apontando para o teu dashboard original
streamlit_process = subprocess.Popen([
    sys.executable, "-m", "streamlit", "run", "dashboard.py",
    "--server.port", porta_nuvem,
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