# Guia de Deploy - Ambientes Grátis

Instruções para colocar **Importa Gastos** em produção com foco em **opções gratuitas**.

## 🎯 Comparativo de Opções Grátis

| Plataforma | FastAPI | PostgreSQL | Preço | Notas |
|-----------|---------|-----------|-------|-------|
| **Render** | ✅ | ✅ (90 dias grátis) | Freemium | **RECOMENDADO** - Melhor free tier |
| **Railway** | ✅ | ✅ | $5-10/mês | Free tier descontinuado, barato |
| **Google Cloud Run** | ✅ | ❌ (Cloud SQL pago) | Free tier | Bom para API, DB pago |
| **PythonAnywhere** | ⚠️ | ⚠️ | Freemium | Limitado para FastAPI |
| **Replit** | ✅ | ✅ | Freemium | Bom para prototipagem |
| **Auto-hospedagem** | ✅ | ✅ | VPS ~$3-5/mês | Máximo controle |

---

## 1️⃣ Render (RECOMENDADO - Melhor Free Tier)

### ✨ Vantagens
- Deploys automáticos via GitHub
- PostgreSQL gratuito por 90 dias (depois $7/mês)
- FastAPI + Streamlit suportados
- Custom domains gratuitos

### 📋 Pré-requisitos
1. Conta GitHub com o repositório do projeto
2. Conta Render (https://render.com)

### 🚀 Passo-a-Passo

#### 1. Preparar o Projeto

**1.1 Criar `Procfile` na raiz:**
```
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.importa_gastos.main:app

**1.1 Comando de inicialização nativo:**
Não é estritamente necessário um Procfile se usarmos o próprio script `app.py` configurado ou o comando direto do Uvicorn no painel do Render:
`uvicorn src.importa_gastos.main:app --host 0.0.0.0 --port 8000`
```

**1.2 Criar `.gitignore` (se não existir):**
```
venv/
__pycache__/
*.pyc
.env
.DS_Store
```

**1.3 Atualizar `requirements.txt`:**
```powershell
.\venv\Scripts\activate
pip install gunicorn uvicorn
pip freeze > requirements.txt
```

**1.4 Adicionar `runtime.txt` na raiz:**
```
python-3.10.13
```

**1.5 Fazer commit e push para GitHub:**
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

#### 2. Criar PostgreSQL no Render

1. Acesse https://dashboard.render.com
2. Clique em **"New +"** → **PostgreSQL**
3. Preencha:
   - **Name:** `financas-db`
   - **Database:** `financas_db`
   - **User:** `postgres`
   - **Region:** Escolha a mais próxima (ex: São Paulo)
4. Clique em **"Create Database"**
5. Copie a **"Internal Database URL"** (aparece após criação)

#### 3. Deploy FastAPI Backend

1. No Render: **"New +"** → **"Web Service"**
2. Conecte seu GitHub
3. Selecione o repositório `importa-gastos`
4. Preencha:
   - **Name:** `importa-gastos-api`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.importa_gastos.main:app`
5. **Environment Variables** (adicione):
   ```
   DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]/financas_db
   ```
   (Use a URL copiada do PostgreSQL)

6. Clique em **"Deploy"**

#### 4. Deploy Streamlit Dashboard

1. No Render: **"New +"** → **"Web Service"**
2. Mesmo repositório
3. Preencha:
   - **Name:** `importa-gastos-dashboard`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run dashboard.py --server.headless true --server.port 10000 --server.address 0.0.0.0`
4. **Environment Variables:**
   ```
    URL_API_BACKEND=https://importa-gastos-api.onrender.com
    DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]/financas_db
   ```
5. Clique em **"Deploy"**

### ✅ Verificar Deployment

- API: https://importa-gastos-api.onrender.com/docs
- Dashboard: https://importa-gastos-dashboard.onrender.com

---

## 2️⃣ Railway (Alternativa Econômica)

### ✨ Vantagens
- Muito simples de usar
- Gratuito com limite de uso ($5 mensais de crédito)
- GitHub integration automática

### 🚀 Setup Rápido

#### 1. Preparar Projeto (mesmo do Render)

#### 2. Conectar GitHub no Railway
1. Acesse https://railway.app
2. Clique em **"New Project"** → **"Deploy from GitHub repo"**
3. Autorize e selecione `importa-gastos`

#### 3. Adicionar Serviços

**PostgreSQL:**
1. Clique em **"Add"** (+ botão)
2. Selecione **PostgreSQL**
3. Railway configura automaticamente

**FastAPI:**
1. Clique em **"Add"** → **"GitHub Repo**
2. Selecione seu repositório
3. Railway detecta `Procfile` automaticamente

#### 4. Environment Variables
1. Na aba **"Variables"** de cada serviço
2. DATABASE_URL, URL_API, etc

#### 5. Deploy
```bash
git push origin main
# Railway detecta automaticamente e faz deploy
```

---

## 3️⃣ Google Cloud Run (Free Tier Generoso)

### ✨ Vantagens
- $300 de crédito grátis para novos usuários
- Sem cartão de crédito por 12 meses
- Escalabilidade automática

### ⚠️ Limitações
- PostgreSQL não é gratuito no GCP
- Usar Firebase Realtime DB ou Firestore (alternativa ao PostgreSQL)

### 🚀 Setup (com Firestore ao invés de PostgreSQL)

#### 1. Instalar Google Cloud SDK
```bash
# Windows
choco install google-cloud-sdk
# ou baixar em: https://cloud.google.com/sdk/docs/install
```

#### 2. Criar Projeto no GCP
```bash
gcloud auth login
gcloud projects create importa-gastos
gcloud config set project importa-gastos
```

#### 3. Dockerizar o Projeto

**Criar `Dockerfile` na raiz:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.importa_gastos.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 4. Deploy para Cloud Run
```bash
gcloud run deploy importa-gastos-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 4️⃣ Auto-hospedagem (VPS Barato)

### Provedores Econômicos
- **Linode:** $5/mês (1GB RAM, 25GB SSD)
- **DigitalOcean:** $4/mês (512MB RAM) - não recomendado
- **Vultr:** $2.50/mês (512MB RAM)
- **Hetzner:** €3/mês (1 vCPU, 2GB RAM)

### 🚀 Setup Básico (Exemplo: Linode)

#### 1. Criar Droplet
- **Image:** Ubuntu 22.04
- **Size:** $5/mês
- **Region:** Próxima a você

#### 2. SSH no Servidor
```bash
ssh root@seu_ip_vps
```

#### 3. Instalar Dependências
```bash
apt update && apt upgrade -y
apt install python3.10 python3-pip postgresql postgresql-contrib nginx -y
```

#### 4. Clonar Projeto
```bash
cd /var/www
git clone https://github.com/seu-usuario/importa-gastos.git
cd importa-gastos
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

#### 5. Configurar PostgreSQL
```bash
sudo -u postgres psql
CREATE DATABASE financas_db;
CREATE USER postgres WITH PASSWORD 'sua_senha_forte';
ALTER ROLE postgres SUPERUSER;
\q
```

#### 6. Criar Systemd Service

**Arquivo: `/etc/systemd/system/importa-gastos.service`**
```ini
[Unit]
Description=Importa Gastos FastAPI
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/importa-gastos
Environment="DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/financas_db"
ExecStart=/var/www/importa-gastos/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.importa_gastos.main:app --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

#### 7. Iniciar Serviço
```bash
systemctl daemon-reload
systemctl start importa-gastos
systemctl enable importa-gastos
```

#### 8. Nginx Reverse Proxy

**Arquivo: `/etc/nginx/sites-available/importa-gastos`**
```nginx
server {
    listen 80;
    server_name seu_dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /dashboard {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
    }
}
```

#### 9. HTTPS com Let's Encrypt
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d seu_dominio.com
```

---

## 🐳 Docker (Opcional - Para Desenvolvimento/Deploy Local)

### `Dockerfile`
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["sh", "-c", "python app.py & streamlit run dashboard.py"]
```

### `docker-compose.yml`
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: 1234
      POSTGRES_DB: financas_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  app:
    build: .
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://postgres:1234@postgres:5432/financas_db
    ports:
      - "8000:8000"
      - "8501:8501"

volumes:
  postgres_data:
```

### Executar Localmente
```bash
docker-compose up --build
```

---

## 🔐 Checklist de Produção

- [ ] `DATABASE_URL` usa senha forte (não `1234`)
- [ ] `HTTPS` habilitado (SSL/TLS)
- [ ] Variáveis sensíveis em `.env` (não no código)
- [ ] `DEBUG=False` em `main.py` para FastAPI
- [ ] Backups automáticos do PostgreSQL configurados
- [ ] Monitoramento de erros ativa (Sentry, etc)
- [ ] Rate limiting em rotas de autenticação
- [ ] CORS configurado apenas para domínios conhecidos

---

## 📊 Recomendação Final

### Para Começar (Sem Custo)
**Render.com** - Melhor relação facilidade/funcionalidade
- PostgreSQL grátis por 90 dias
- Deploy automático via GitHub
- Custom domains inclusos

### Para Longo Prazo (Mínimo Custo)
**VPS Barato** (~$5/mês) + Seu próprio servidor
- Máximo controle
- Custo previsível
- Ideal para aprender DevOps

### Para Prototipagem Rápida
**Replit** - Setup em minutos, sem configuração

---

## 🆘 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'src'"
**Solução:** Ensure working directory é a raiz do projeto em deployment

### Erro: "DATABASE_URL not set"
**Solução:** Adicione variável de ambiente na plataforma de deploy

### Streamlit conectando lentamente
**Solução:** Aumente timeout em `dashboard.py`:
```python
requests.get(url, timeout=30.0)
```

### PostgreSQL fora do ar em Render
**Solução:** Upgrade para plano pago ($7/mês) após 90 dias de free tier