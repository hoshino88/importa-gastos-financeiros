import unittest

from src.importa_gastos.parsers import filtrar_dados_fatura


class FiltrarDadosFaturaTests(unittest.TestCase):
    def test_extrai_campos_de_pix(self):
        texto = (
            "Comprovante de Pagamento Pix\n"
            "Pagamento supermercado\n"
            "Valor:\n"
            "R$ 123,45\n"
            "Realizado em: 01/06/2026\n"
            "Instituição do pagador: Banco Exemplo\n"
        )

        dados = filtrar_dados_fatura(texto)

        self.assertEqual(dados["descricao"], "Pagamento supermercado")
        self.assertEqual(dados["valor"], 123.45)
        self.assertEqual(dados["data_transacao"], "01/06/2026")
        self.assertEqual(dados["instituicao_pagador"], "Banco Exemplo")

    def test_extrai_campos_de_boleto(self):
        texto = (
            "12345-6 Conta Origem:\n"
            "Banco Exemplo Instituição Emissora:\n"
            "EMPRESA TESTE Razão Social Beneficiário:\n"
            "99,90 Valor Pago\n"
            "Pagamento da mensalidade Descrição do Pagamento:\n"
            "01/06/2026Data da Transação:\n"
            "15/06/2026Data de Vencimento:\n"
            "Conta Corrente:\n"
        )

        dados = filtrar_dados_fatura(texto)

        self.assertEqual(dados["conta_origem"], "12345-6")
        self.assertEqual(dados["instituicao_emissora"], "Banco Exemplo")
        self.assertEqual(dados["razao_social_beneficiario"], "EMPRESA TESTE")
        self.assertEqual(dados["valor_pago"], 99.9)
        self.assertEqual(dados["descricao"], "Pagamento da mensalidade")
        self.assertEqual(dados["data_transacao"], "01/06/2026")
        self.assertEqual(dados["data_vencimento"], "15/06/2026")
        self.assertEqual(dados["tipo_conta"], "Conta Corrente")


if __name__ == "__main__":
    unittest.main()
