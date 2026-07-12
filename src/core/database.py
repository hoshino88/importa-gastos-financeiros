from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# URL de conexão local padrão do PostgreSQL
# Formato: postgresql://usuario:senha@servidor:porta/nome_do_banco
# NOTA: Quando você instalar o Postgres no Windows, mudaremos a 'sua_senha' aqui
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/financas_db"

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