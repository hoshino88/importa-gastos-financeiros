import enum
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base

# Definindo as opções permitidas para os Enums
class TipoTransacaoEnum(str, enum.Enum):
    BOLETO = "BOLETO"
    PIX = "PIX"
    DESCONHECIDO = "DESCONHECIDO"

class TipoContaEnum(str, enum.Enum):
    CORRENTE = "CORRENTE"
    POUPANCA = "POUPANÇA"
    OUTRA = "OUTRA"

# 🔐 NOVA TABELA: Armazena as informações de login dos usuários
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)  # Armazenará a senha criptografada com segurança
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    # Relação: Permite buscar todas as transações de um usuário facilmente (ex: usuario.transacoes)
    transacoes = relationship("TransacaoFinanceira", back_populates="usuario", cascade="all, delete-orphan")


class TransacaoFinanceira(Base):
    __tablename__ = "transacoes_financeiras"

    id = Column(Integer, primary_key=True, index=True)
    
    # 👈 CHAVE ESTRANGEIRA: Vincula obrigatoriamente cada transação a um usuário da tabela de usuários
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Usando os Enums
    tipo_transacao = Column(Enum(TipoTransacaoEnum), nullable=False, index=True)
    tipo_conta_origem = Column(Enum(TipoContaEnum), nullable=True, index=True)
    
    # --- DADOS DE ORIGEM ---
    conta_origem = Column(String, nullable=True)      # Ex: 37052-8
    cooperativa_origem = Column(String, nullable=True)
    instituicao_pagador = Column(String, nullable=True)# Geralmente Sicredi
    
    # --- DADOS DE DESTINO ---
    destinatario_nome = Column(String, nullable=False) # Nome ou Razão Social
    
    # --- DETALHES DO PAGAMENTO ---
    valor = Column(Float, nullable=False)
    data_transacao = Column(Date, nullable=False)
    data_vencimento = Column(Date, nullable=True)     # Exclusivo de Boleto
    descricao = Column(String, nullable=True)
    
    # --- METADADOS ---
    nome_arquivo = Column(String, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    # Relação: Permite acessar o objeto do usuário direto da transação (ex: transacao.usuario.username)
    usuario = relationship("Usuario", back_populates="transacoes")