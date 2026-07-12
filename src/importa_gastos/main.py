from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Annotated

from fastapi import Depends, FastAPI, File, UploadFile, HTTPException, status
from pydantic import BaseModel
from pypdf import PdfReader
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from src.core.database import Base, engine, get_db
# Importando o modelo de Usuario, TransacaoFinanceira e os Enums
from src.importa_gastos.models import (
    Usuario,
    TipoContaEnum,
    TipoTransacaoEnum,
    TransacaoFinanceira,
)
from src.importa_gastos.parsers import filtrar_dados_fatura

# Configuração do utilitário de criptografia de senhas (Hash seguro)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schemas do Pydantic para validação dos payloads recebidos no Login e Cadastro
class UsuarioAuthSchema(BaseModel):
    username: str
    password: str

def create_app() -> FastAPI:
    app = FastAPI(title="Importa Gastos")

    # Garante a criação das novas tabelas estruturadas (usuarios e transacoes) no Postgres
    Base.metadata.create_all(bind=engine)

    # --- 🔐 ROTA DE CADASTRO (CRIAR CONTA) ---
    @app.post("/auth/cadastro", status_code=status.HTTP_201_CREATED)
    def cadastrar_usuario(dados: UsuarioAuthSchema, db: Session = Depends(get_db)):
        # 1. Verifica se o usuário já existe na base de dados
        usuario_existente = db.query(Usuario).filter(Usuario.username == dados.username).first()
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Este nome de usuário já está em uso."
            )
        
        # 2. Criptografa a senha antes de salvar
        senha_criptografada = pwd_context.hash(dados.password)
        
        # 3. Cria e persiste o novo registro
        novo_usuario = Usuario(
            username=dados.username,
            senha_hash=senha_criptografada
        )
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        
        return {"mensagem": "Usuário criado com sucesso!", "usuario_id": novo_usuario.id}

    # --- 🗝️ ROTA DE LOGIN (AUTENTICAR) ---
    @app.post("/auth/login")
    def login_usuario(dados: UsuarioAuthSchema, db: Session = Depends(get_db)):
        # 1. Busca o usuário pelo nome cadastrado
        usuario = db.query(Usuario).filter(Usuario.username == dados.username).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Usuário ou senha incorretos."
            )
        
        # 2. Verifica se a senha enviada é idêntica ao hash salvo no Postgres
        senha_valida = pwd_context.verify(dados.password, usuario.senha_hash)
        if not senha_valida:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Usuário ou senha incorretos."
            )
        
        # 3. Retorna os metadados da sessão para o Streamlit salvar no session_state
        return {
            "mensagem": "Login realizado com sucesso!",
            "usuario_id": usuario.id,
            "username": usuario.username
        }

    # --- 📥 ROTA DE IMPORTAÇÃO (VINCULADA AO USUÁRIO) ---
    @app.post("/importar-faturas")
    async def importar_faturas(
        usuario_id: int,  # 👈 PARÂMETRO OBRIGATÓRIO: Recebe o ID do usuário logado
        arquivos: Annotated[list[UploadFile], File(...)],
        db: Session = Depends(get_db),
    ):
        # Validação preventiva: garante que o usuário realmente existe antes de iterar os PDFs
        usuario_valido = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario_valido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Usuário não identificado. Faça login novamente."
            )

        resultados: list[dict[str, object]] = []

        for arquivo in arquivos:
            conteudo_pdf = await arquivo.read()
            leitor = PdfReader(BytesIO(conteudo_pdf))

            texto_completo = ""
            for pagina in leitor.pages:
                texto_completo += (pagina.extract_text() or "") + "\n"

            # Executa o seu Regex estruturado
            dados_processados = filtrar_dados_fatura(texto_completo)
            
            # Descobre se o PDF lido era um boleto ou pix
            tipo_doc = dados_processados.get("tipo_documento", "").upper()

            # Criação do objeto mapeado dependendo do tipo
            if tipo_doc == "BOLETO":
                # Tratamento para mapear a String do tipo de conta para o Enum correspondente
                tipo_conta_str = dados_processados.get("tipo_conta", "").upper()
                tipo_conta_enum = TipoContaEnum.CORRENTE if "CORRENTE" in tipo_conta_str else (
                                  TipoContaEnum.POUPANCA if "POUPANCA" in tipo_conta_str else TipoContaEnum.OUTRA)

                nova_transacao = TransacaoFinanceira(
                    usuario_id=usuario_id,  # 👈 Chave estrangeira injetada aqui
                    tipo_transacao=TipoTransacaoEnum.BOLETO,
                    tipo_conta_origem=tipo_conta_enum,
                    conta_origem=dados_processados.get("conta_origem"),
                    instituicao_pagador=dados_processados.get("instituicao_pagador"),
                    destinatario_nome=dados_processados.get("razao_social_beneficiario", "Desconhecido"),
                    valor=float(dados_processados.get("valor", 0.0)),
                    descricao=dados_processados.get("descricao"),
                    data_transacao=datetime.strptime(str(dados_processados.get("data_transacao")), "%d/%m/%Y").date(),
                    data_vencimento=datetime.strptime(str(dados_processados.get("data_vencimento")), "%d/%m/%Y").date(),
                    nome_arquivo=arquivo.filename or "desconhecido",
                )
                
            elif tipo_doc == "PIX":
                nova_transacao = TransacaoFinanceira(
                    usuario_id=usuario_id,  # 👈 Chave estrangeira injetada aqui
                    tipo_transacao=TipoTransacaoEnum.PIX,
                    cooperativa_origem=dados_processados.get("cooperativa_origem"),
                    conta_origem=dados_processados.get("conta_origem"),
                    instituicao_pagador=dados_processados.get("instituicao_pagador"),
                    destinatario_nome=dados_processados.get("nome_destinatario", "Desconhecido"),
                    valor=float(dados_processados.get("valor", 0.0)),
                    data_transacao=datetime.strptime(str(dados_processados.get("data_transacao")), "%d/%m/%Y").date(),
                    descricao=dados_processados.get("descricao"),
                    nome_arquivo=arquivo.filename or "desconhecido",
                )
            else:
                # Se cair aqui, o PDF não foi identificado como boleto ou pix válido
                continue

            # Adiciona a transação na fila do banco de dados
            db.add(nova_transacao)
            
            # Adiciona ao retorno da API
            dados_processados["nome_arquivo"] = arquivo.filename
            resultados.append(dados_processados)

        # Salva em lote no Postgres
        db.commit()

        return {
            "status": "sucesso",
            "mensagem": f"{len(resultados)} documento(s) salvo(s) com sucesso!",
            "dados": resultados
        }

    return app

app = create_app()