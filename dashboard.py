import streamlit as str_ui
import httpx
import pandas as pd
import os
from sqlalchemy import create_engine, text
from src.core.database import DATABASE_URL

# --- CONFIGURAÇÕES INICIAIS ---
str_ui.set_page_config(page_title="Gerenciador Finanças", page_icon="💰", layout="wide")
engine = create_engine(DATABASE_URL)

# Pega a URL dinâmica configurada no run.py. 
# Se você estiver rodando localmente no VS Code sem o run.py, ele usa o padrão 127.0.0.1:8080
URL_API = os.getenv("URL_API_BACKEND", "http://127.0.0.1:8080")

if "logado" not in str_ui.session_state:
    str_ui.session_state.update({"logado": False, "usuario_id": None, "username": ""})

# --- FUNÇÃO AUXILIAR PARA CHAMADAS DA API (LOGIN/CADASTRO) ---
def autenticar(endpoint, username, password):
    try:
        res = httpx.post(f"{URL_API}/auth/{endpoint}", json={"username": username, "password": password}, timeout=10.0)
        if res.status_code in [200, 201]:
            dados = res.json()
            str_ui.session_state.update({"logado": True, "usuario_id": dados.get("usuario_id"), "username": username})
            str_ui.success("Sucesso! Entrando no sistema...")
            str_ui.rerun()
        else:
            str_ui.error(f"❌ {res.json().get('detail', 'Erro na operação.')}")
    except Exception as e:
        str_ui.error(f"❌ Erro de conexão: {e}")

# ==============================================================================
# TELA DE ACESSO (LOGIN / CADASTRO UNIFICADOS)
# ==============================================================================
if not str_ui.session_state.logado:
    str_ui.title("🔐 Controle de Finanças - Acesso")
    
    with str_ui.form("form_acesso"):
        user = str_ui.text_input("Usuário")
        senha = str_ui.text_input("Senha", type="password")
        c1, c2 = str_ui.columns(2)
        
        with c1: btn_login = str_ui.form_submit_button("Entrar na Conta", type="primary", use_container_width=True)
        with c2: btn_cad = str_ui.form_submit_button("Criar Nova Conta", use_container_width=True)
        
        if (btn_login or btn_cad) and (not user or not senha):
            str_ui.warning("Preencha todos os campos.")
        elif btn_login:
            autenticar("login", user, senha)
        elif btn_cad:
            autenticar("cadastro", user, senha)

# ==============================================================================
# DASHBOARD PRINCIPAL (USUÁRIO LOGADO)
# ==============================================================================
else:
    with str_ui.sidebar:
        str_ui.markdown(f"👤 Usuário: **{str_ui.session_state.username}**")
        if str_ui.button("🚪 Sair", use_container_width=True):
            str_ui.session_state.update({"logado": False, "usuario_id": None, "username": ""})
            str_ui.rerun()

    aba_upload, aba_banco = str_ui.tabs(["📤 Importar PDFs", "🗄️ Gerenciar Banco"])

    # --- ABA 1: UPLOAD ---
    with aba_upload:
        str_ui.title("💰 Importação de Gastos")
        arquivos = str_ui.file_uploader("Selecione os PDFs", type=["pdf"], accept_multiple_files=True)

        if arquivos and str_ui.button("🚀 Processar e Salvar", type="primary"):
            with str_ui.spinner("Processando..."):
                try:
                    arquivos_api = [("arquivos", (arq.name, arq.getvalue(), "application/pdf")) for arq in arquivos]
                    res = httpx.post(f"{URL_API}/importar-faturas?usuario_id={str_ui.session_state.usuario_id}", files=arquivos_api, timeout=60.0)
                    
                    if res.status_code == 200:
                        str_ui.success(f"✅ {res.json().get('mensagem')}")
                        df = pd.DataFrame(res.json().get("dados", []))
                        if not df.empty:
                            df["Favorecido"] = df.get("razao_social_beneficiario", df.get("nome_destinatario", "Desconhecido")).fillna("Desconhecido")
                            df["Valor"] = df["valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                            df_exibicao = df[["nome_arquivo", "tipo_documento", "Valor", "data_transacao", "Favorecido"]].copy()
                            df_exibicao.columns = ["Arquivo Origem", "Tipo", "Valor", "Data", "Favorecido"]
                            str_ui.dataframe(df_exibicao, use_container_width=True, hide_index=True)
                    else:
                        str_ui.error(f"Erro: {res.json().get('detail')}")
                except Exception as e:
                    str_ui.error(f"Falha: {e}")

    # --- ABA 2: GERENCIAR BANCO ---
    with aba_banco:
        str_ui.title("🗄️ Histórico de Dados")

        # Área de Deleção
        with str_ui.expander("🗑️ Remover Arquivos", expanded=False):
            with engine.connect() as conn:
                arquivos_eb = [r[0] for r in conn.execute(text("SELECT DISTINCT nome_arquivo FROM transacoes_financeiras WHERE usuario_id = :id;"), {"id": str_ui.session_state.usuario_id})]
            
            if arquivos_eb:
                c1, c2 = str_ui.columns([3, 1])
                sel = c1.selectbox("Arquivo:", arquivos_eb, index=None, label_visibility="collapsed")
                if c2.button("Excluir", type="primary", disabled=not sel, use_container_width=True):
                    with engine.connect() as conn:
                        conn.execute(text("DELETE FROM transacoes_financeiras WHERE nome_arquivo = :n AND usuario_id = :id;"), {"n": sel, "id": str_ui.session_state.usuario_id})
                        conn.commit()
                    str_ui.rerun()
            else:
                str_ui.write("Nenhum arquivo encontrado.")

        # Exibição da Tabela
        str_ui.subheader("📊 Suas Transações")
        try:
            df_final = pd.read_sql_query(text("SELECT * FROM transacoes_financeiras WHERE usuario_id = :id ORDER BY criado_em DESC;"), con=engine, params={"id": str_ui.session_state.usuario_id})
            if not df_final.empty:
                str_ui.metric("Gasto Total", f"R$ {df_final['valor'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                df_final["Valor"] = df_final["valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                df_banco = df_final[["nome_arquivo", "tipo_transacao", "conta_origem", "Valor", "data_transacao", "destinatario_nome", "instituicao_pagador", "descricao"]].copy()
                df_banco.columns = ["Arquivo", "Tipo", "Conta", "Valor", "Data", "Favorecido", "Banco", "Descrição"]
                str_ui.dataframe(df_banco, use_container_width=True, hide_index=True)
            else:
                str_ui.warning("Nenhuma transação cadastrada.")
        except Exception as e:
            str_ui.error(f"Erro ao ler banco: {e}")