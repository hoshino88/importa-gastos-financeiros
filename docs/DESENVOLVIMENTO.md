# Guia de Desenvolvimento

Instruções para desenvolvedores que trabalham no projeto **Importa Gastos**.

## 🔧 Setup Inicial

### 1. Clonar e Ambiente

```powershell
git clone <repo-url>
cd importa-gastos
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

⚠️ Nota para Windows: Se encontrar o erro ValueError: password cannot be longer than 72 bytes ao cadastrar usuários, certifique-se de que a versão do bcrypt instalada é exatamente a 4.0.1 (pip install bcrypt==4.0.1).

### 2. PostgreSQL

Se não tiver PostgreSQL instalado:
1. Baixe em: https://www.postgresql.org/download/windows/
2. Durante instalação, anote a senha do usuário `postgres`
3. Crie o banco:

```sql
psql -U postgres
CREATE DATABASE financas_db;
\q
```

### 3. Configurar Credenciais

Edite `src/core/database.py`:
```python
DATABASE_URL = "postgresql://postgres:SUA_SENHA@localhost:5432/financas_db"
```

## 📂 Estrutura de Desenvolvimento

```
importa-gastos/
├── app.py                          # FastAPI entry point
├── dashboard.py                    # Streamlit interface
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   └── database.py            # SQLAlchemy + PostgreSQL
│   └── importa_gastos/
│       ├── __init__.py
│       ├── main.py                # FastAPI routes + auth
│       ├── models.py              # ORM models (Usuario, Transacao)
│       └── parsers.py             # PDF parsing logic
├── tests/
│   └── test_parsers.py            # Unit tests
├── samples/                        # Example PDFs
└── docs/
    ├── estrutura.md               # Architecture overview
    ├── DESENVOLVIMENTO.md         # This file
    └── README.md                  # User guide
```

## 🚀 Executar Localmente

### Terminal 1 - FastAPI Backend
```powershell
.\venv\Scripts\activate
python app.py
# → Acesse http://127.0.0.1:8000/docs
```

### Terminal 2 - Streamlit Dashboard
```powershell
.\venv\Scripts\activate
streamlit run dashboard.py
# → Acesse http://localhost:8501
```

## 📝 Workflow Típico

### Adicionar Nova Rota FastAPI

1. **Edite `src/importa_gastos/main.py`:**
```python
@app.post("/nova-rota")
def minha_rota(dados: MeuSchema, db: Session = Depends(get_db)):
    # Sua lógica aqui
    return {"status": "ok"}
```

2. **Teste em http://127.0.0.1:8000/docs**

### Modificar Modelo de Dados

1. **Edite `src/importa_gastos/models.py`:**
```python
class MinhaTabela(Base):
    __tablename__ = "minha_tabela"
    # Seus campos aqui
```

2. **SQLAlchemy criará automaticamente ao reiniciar `main.py`**

3. **Atualize a lógica em `main.py`** se necessário

### Adicionar Testes

1. **Crie testes em `tests/test_novos.py`:**
```python
def test_parser_novo():
    resultado = parsers.funcao_nova()
    assert resultado is not None
```

2. **Execute:**
```powershell
pytest tests/ -v
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'src'"
**Solução:** Certifique-se de:
- Estar na pasta raiz do projeto
- Usar Python do venv: `.\venv\Scripts\python.exe`

### "connection refused" (PostgreSQL)
**Solução:**
```powershell
# Windows - verificar se o serviço está rodando
Get-Service postgresql-x64-15  # (ajuste versão)
Start-Service postgresql-x64-15
```

### Dashboard não conecta à API
**Solução:**
- Certifique-se que `python app.py` está rodando
- Verifique a URL em `dashboard.py`: `URL_API = "http://127.0.0.1:8000"`

### Erro de permissão ao fazer upload
**Solução:**
- Crie a pasta `samples/` se não existir
- Verifique permissões de escrita no diretório

## 📊 Alterações Recentes

### ✨ Versão Atual (Com Autenticação e Banco)
- ✅ Sistema completo de autenticação (cadastro + login)
- ✅ PostgreSQL com SQLAlchemy ORM
- ✅ Dashboard Streamlit funcional
- ✅ Modelos de Usuário e Transação Financeira
- ✅ Suporte a BOLETO e PIX

### 🔜 Próximos Passos Recomendados
- [ ] Adicionar refresh tokens JWT
- [ ] Implementar relatórios por período
- [ ] Adicionar exportação para Excel/CSV
- [ ] Melhorar detecção de fraudes
- [x] Deploy em ambientes grátis (Veja [docs/DEPLOY.md](DEPLOY.md))

## 🔐 Checklist de Segurança

- [x] Senhas criptografadas com bcrypt
- [x] Validação de entrada (Pydantic schemas)
- [ ] Rate limiting em rotas de autenticação
- [ ] HTTPS em produção
- [ ] CORS configurado adequadamente
- [ ] SQL injection prevenido (SQLAlchemy parameterizado)

## 📚 Recursos Úteis

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Streamlit Guide](https://docs.streamlit.io/)
- [PyPDF Documentation](https://pypdf.readthedocs.io/)
- [PostgreSQL Tutorial](https://www.postgresql.org/docs/)

## 👥 Contatos / Notas

- Banco padrão: `financas_db`
- Senha PostgreSQL local: `1234`
- Port API: `8000`
- Port Streamlit: `8501`
