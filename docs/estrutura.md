# Estrutura do Projeto

Arquitetura modular com FastAPI backend, PostgreSQL persistência, autenticação segura e dashboard Streamlit.

## Pastas e Arquivos Principais

### Configuração e Entry Points
- **`app.py`**: Entry point para executar o servidor FastAPI
- **`dashboard.py`**: Interface web (Streamlit) para usuários finais

### Backend (`src/`)

#### `src/core/`
- **`database.py`**: Configuração SQLAlchemy, conexão PostgreSQL e SessionLocal

#### `src/importa_gastos/`
- **`main.py`**: API FastAPI com rotas de autenticação e processamento de faturas
- **`models.py`**: Modelos ORM (Usuario, TransacaoFinanceira) com enums para tipos
- **`parsers.py`**: Regras de extração e normalização de dados de PDFs (BOLETO, PIX)

### Testes e Exemplos
- **`tests/`**: Testes unitários do parser
- **`samples/`**: PDFs de exemplo para validação manual
- **`docs/`**: Documentação complementar

## Arquitetura do Fluxo

### 1️⃣ Autenticação
```
POST /auth/cadastro  → Criar nova conta (username + password com bcrypt)
POST /auth/login     → Fazer login (retorna usuario_id)
```

### 2️⃣ Processamento de Faturas
```
POST /importar-faturas (autenticado)
  ↓
Recebe um ou mais PDFs
  ↓
Parser identifica formato (BOLETO ou PIX)
  ↓
Extrai campos: tipo_conta, conta, instituição, valor, data, etc
  ↓
Salva em PostgreSQL (transacoes_financeiras)
  ↓
Retorna JSON com dados processados
```

### 3️⃣ Dashboard Streamlit
```
Autenticação de usuário (login/cadastro)
  ↓
Upload de múltiplos PDFs
  ↓
Processamento via API
  ↓
Visualização em tabela (histórico de transações)
  ↓
Opções de deleção/gerenciamento
```

## Modelo de Dados

### Usuários (`usuarios`)
- `id` (PK)
- `username` (unique)
- `senha_hash` (bcrypt)
- `criado_em` (timestamp)

### Transações Financeiras (`transacoes_financeiras`)
- `id` (PK)
- `usuario_id` (FK → usuarios)
- `tipo_transacao` (BOLETO, PIX, DESCONHECIDO)
- `tipo_conta_origem` (CORRENTE, POUPANÇA, OUTRA)
- `conta_origem`, `instituicao_pagador`, `instituicao_emissora`
- `destinatario_nome`, `valor`, `data_transacao`, `data_vencimento`
- `descricao`, `nome_arquivo`, `criado_em`
