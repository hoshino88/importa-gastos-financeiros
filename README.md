# Importa Gastos

Aplicação FastAPI + Streamlit para extrair dados de faturas e comprovantes em PDF, com autenticação de usuários e persistência em PostgreSQL.

## 🎯 Visão Geral

O projeto permite que usuários façam upload de PDFs de faturas (BOLETO, PIX), os quais são processados, extraídos e armazenados em banco de dados. Inclui:
- ✅ **Autenticação segura** com hash de senhas (bcrypt)
- ✅ **Dashboard Streamlit** para interface visual
- ✅ **PostgreSQL** para persistência de dados
- ✅ **API FastAPI** para processamento de PDFs
- ✅ **Suporte a múltiplos formatos** de faturas

## 📁 Estrutura e Documentação

Veja [docs/estrutura.md](docs/estrutura.md) para detalhes completos.

- **`app.py`**: Entry point FastAPI (execução com `python app.py`)
- **`dashboard.py`**: Interface Streamlit para usuários
- **`src/importa_gastos/`**: Lógica de parsing e modelos
- **`src/core/database.py`**: Configuração PostgreSQL + SQLAlchemy
- **`samples/`**: PDFs de exemplo para testes manuais
- **`tests/`**: Testes unitários

### 📚 Documentação Complementar
- **[docs/DESENVOLVIMENTO.md](docs/DESENVOLVIMENTO.md)** - Setup local, workflow de desenvolvimento, troubleshooting
- **[docs/DEPLOY.md](docs/DEPLOY.md)** - Deploy em ambientes grátis (Render, Railway, etc)

## 🚀 Instalação Rápida

### 1. Pré-requisitos
- Python 3.10+
- PostgreSQL 12+

### 2. Clonar e Ambiente Virtual

```powershell
# Criar ambiente virtual
python -m venv venv
.\venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. PostgreSQL Local

Caso tenha bloqueios de política no PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Configuração do banco:**
```sql
CREATE DATABASE financas_db;
```

Credenciais padrão (em `src/core/database.py`):
- **Host:** localhost
- **Port:** 5432
- **User:** postgres
- **Password:** 1234
- **Database:** financas_db

## ▶️ Execução

### FastAPI Backend
```powershell
python app.py
```
Acesse a documentação interativa: `http://127.0.0.1:8000/docs`

**Endpoints principais:**
- `POST /auth/cadastro` - Criar conta
- `POST /auth/login` - Fazer login
- `POST /importar-faturas` - Upload e processamento de PDFs (autenticado)

### Dashboard Streamlit
```powershell
streamlit run dashboard.py
```
Acessível em: `http://localhost:8501`

**Funcionalidades:**
- Login/Cadastro integrado
- Upload múltiplo de PDFs
- Visualização de transações em tabela
- Gerenciamento (filtros, deleção)

## 🔐 Autenticação

### Cadastro
```bash
curl -X POST "http://127.0.0.1:8000/auth/cadastro" \
  -H "Content-Type: application/json" \
  -d '{"username":"seu_usuario","password":"sua_senha"}'
```

### Login
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"seu_usuario","password":"sua_senha"}'
```

Retorna: `{"usuario_id": 1}` (use em headers de autenticação)

## 📊 Processamento de Faturas

### Tipos Suportados
- **BOLETO**: Extrai `tipo_conta_origem`, `conta_origem`, `instituição_pagador`, `valor`, `data_vencimento`
- **PIX**: Extrai informações de transferência PIX processada

### Fluxo de Processamento
1. Upload de 1+ PDFs via `/importar-faturas`
2. Parser detecta formato automaticamente
3. Dados são normalizados e validados
4. Salvos em `transacoes_financeiras` no PostgreSQL
5. Resposta retorna dados extraídos em JSON

## 🧪 Testes

```powershell
pytest tests/test_parsers.py -v
```

## 📝 Notas de Desenvolvimento

- Use o Python do `venv` (`.\venv\Scripts\python.exe`), não o `py` do sistema
- As migrações do banco são automáticas (SQLAlchemy `create_all`)
- PDFs de exemplo estão em `samples/`
- Senhas são criptografadas com bcrypt antes de armazenamento

## 📦 Dependências Principais

- **FastAPI** - Web framework
- **Streamlit** - Dashboard web
- **SQLAlchemy** - ORM
- **psycopg2** - Driver PostgreSQL
- **passlib** - Gerenciamento de senhas
- **pypdf** - Leitura de PDFs