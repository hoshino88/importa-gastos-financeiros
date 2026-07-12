from __future__ import annotations

import re


def filtrar_dados_fatura(texto: str) -> dict[str, object]:
    dados: dict[str, object] = {}
    dados["tipo_documento"] = "BOLETO" if "Boleto" in texto else "PIX" if "Comprovante de Pagamento Pix" in texto else "DESCONHECIDO"

    if dados["tipo_documento"] == "PIX":
        # Pega cooperativa e conta origem
        padrao_coop_conta = r"Cooperativa e conta origem:\s*(\d{4})/(\d{5}-\d{1})"
        busca_coop_conta = re.search(padrao_coop_conta, texto)
        dados["conta_origem"] = (busca_coop_conta.group(2) if busca_coop_conta else "Não encontrado")
        dados["cooperativa_origem"] = (busca_coop_conta.group(1) if busca_coop_conta else "Não encontrado")

        # Pega o nome do destinatário
        padrao_destinatario = r"Nome do destinatário:\s*(.+?)\s*\n"
        busca_destinatario = re.search(padrao_destinatario, texto)
        dados["nome_destinatario"] = (
            busca_destinatario.group(1).strip() if busca_destinatario else "Não encontrado"
        )

        # Pega a descrição do pagamento Pix
        padrao_desc = r"Comprovante de Pagamento Pix\s*\n\s*(.+?)\s*\n\s*Valor:"
        busca_desc = re.search(padrao_desc, texto)
        dados["descricao"] = (
            busca_desc.group(1).strip() if busca_desc else "Não encontrado"
        )

        # Pega o valor do pagamento Pix
        padrao_valor = r"Valor:\s*R\$\s*(\d+,\d{2})"
        busca_valor = re.search(padrao_valor, texto)
        dados["valor"] = busca_valor.group(1) if busca_valor else "Não encontrado"

        # Pega a data da transação Pix
        padrao_data = r"Realizado em:\s*(\d{2}/\d{2}/\d{4})"
        busca_data = re.search(padrao_data, texto)
        dados["data_transacao"] = (
            busca_data.group(1) if busca_data else "Não encontrado"
        )

        # Pega a instituição do pagador
        padrao_inst_pagador = r"Instituição do pagador:\s*(.+?)\s*\n"
        busca_inst_pagador = re.search(padrao_inst_pagador, texto)
        dados["instituicao_pagador"] = (
            busca_inst_pagador.group(1).strip() if busca_inst_pagador else "Não encontrado"
        )
    else:
        # --- Padrões para o PDFs Boleto ---
        
        # 👈 CORREÇÃO: Ajustado para if/elif/else para não sobrescrever o tipo de conta
        if "Conta Corrente" in texto:
            dados["tipo_conta"] = "Conta Corrente"
        elif "Conta Poupança" in texto:
            dados["tipo_conta"] = "Conta Poupança"
        else:
            dados["tipo_conta"] = "Outro tipo"

        # Conta Origem (Tratamento de inversão)
        padrao_conta = r"(\d{5}-\d{1})\s*Conta\s*Origem:|Conta\s*Origem:\s*(\d{5}-\d{1})"
        busca_conta = re.search(padrao_conta, texto, re.IGNORECASE)
        if busca_conta:
            dados["conta_origem"] = (busca_conta.group(1) or busca_conta.group(2)).strip()

        # Instituição Emissora
        padrao_inst_emissora = r"(.+?)\s*Instituição\s*Emissora:|Instituição\s*Emissora:\s*(.+?)\s*\n"
        busca_inst_emissora = re.search(padrao_inst_emissora, texto, re.IGNORECASE)
        if busca_inst_emissora:
            dados["instituicao_pagador"] = (
                busca_inst_emissora.group(1) or busca_inst_emissora.group(2)
            ).strip()

        # Razão Social Beneficiário
        padrao_razao_social = r"([A-Z\s]{4,})Razão\s*Social\s*Beneficiário:|Razão\s*Social\s*Beneficiário:\s*([A-Z\s]{4,})"
        busca_razao_social = re.search(padrao_razao_social, texto, re.IGNORECASE)
        if busca_razao_social:
            dados["razao_social_beneficiario"] = (
                busca_razao_social.group(1) or busca_razao_social.group(2)
            ).strip()

        # Valor Pago unificado na chave "valor"
        padrao_valor = r"(\d+,\d{2})\s*Valor\s*Pago|Valor\s*Pago\s*(?:\(R\$\))?:\s*(\d+,\d{2})"
        busca_valor = re.search(padrao_valor, texto, re.IGNORECASE)
        if busca_valor:
            dados["valor"] = (
                busca_valor.group(1) or busca_valor.group(2)
            ).strip()

        # Descrição do Boleto
        padrao_desc_boleto = r"(.+?)\s*Descrição\s*do\s*Pagamento:|Descrição\s*do\s*Pagamento:\s*(.+?)\s*\n"
        busca_desc_boleto = re.search(padrao_desc_boleto, texto, re.IGNORECASE)
        if busca_desc_boleto:
            dados["descricao"] = (
                busca_desc_boleto.group(1) or busca_desc_boleto.group(2)
            ).strip()

        # Datas do Boleto
        padrao_datas = r"(\d{2}/\d{2}/\d{4})Data da Transação:\s*\n\s*(\d{2}/\d{2}/\d{4})Data de Vencimento:"
        busca_datas = re.search(padrao_datas, texto)
        if busca_datas:
            dados["data_transacao"] = busca_datas.group(1)
            dados["data_vencimento"] = busca_datas.group(2)
        else:
            dados["data_transacao"] = "Não encontrado"
            dados["data_vencimento"] = "Não encontrado"

    # --- Sanitização Final dos Valores ---
    # 👈 CORREÇÃO: Alinhamento da indentação corrigido no bloco principal
    if dados.get("valor") and dados["valor"] != "Não encontrado":
        valor_limpo = str(dados["valor"]).replace(".", "").replace(",", ".")
        dados["valor"] = float(valor_limpo)
    else:
        dados["valor"] = 0.0

    return dados