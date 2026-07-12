import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Tenta buscar a variável DATABASE_URL da Railway/Neon. 
# Se não encontrar (como quando você roda localmente no VS Code), ele usa o seu banco local como plano B!
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:1234@localhost:5432/financas_db"
)

# 2. Pequeno ajuste de segurança para garantir compatibilidade com o SQLAlchemy na nuvem
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# O motor que gerencia as conexões físicas com o banco
engine = create_engine(DATABASE_URL)

# Criador de sessões (usado para abrir e fechar conversas com o banco)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# A classe base que todas as nossas tabelas vão herdar
Base = declarative_base()


# Função que o FastAPI vai usar para abrir o banco no início de uma rota e fechar no final
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()