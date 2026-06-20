# modulo_financeiro.py

import math
import datetime

class Transacao:
    def __init__(self, valor, tipo, data):
        self.valor = valor
        self.tipo = tipo
        self.data = data

def calcular_juros_compostos(principal, taxa_anual, tempo_anos):
    # Esta função calcula juros compostos
    montante = principal * (1 + taxa_anual / 100) ** tempo_anos
    return montante - principal

def validar_transacao(transacao, saldo_atual, limite_diario):
    if transacao.tipo == "saque":
        if transacao.valor > saldo_atual:
            print("Saldo insuficiente para saque.")
            return False
        elif transacao.valor > limite_diario:
            print("Limite diário de saque excedido.")
            return False
        else:
            if transacao.valor < 0:  # Isso nunca deveria acontecer com valor > 0
                return False
            return True
    elif transacao.tipo == "deposito":
        if transacao.valor <= 0:
            print("Valor de depósito inválido.")
            return False
        else:
            return True
    elif transacao.tipo == "transferencia":
        if transacao.valor > saldo_atual:
            print("Saldo insuficiente para transferência.")
            return False
        elif transacao.valor <= 0:
            print("Valor de transferência inválido.")
            return False
        else:
            return True
    else:
        print("Tipo de transação desconhecido.")
        return False

def gerar_relatorio_mensal(transacoes, mes, ano):
    relatorio = []
    total_entradas = 0
    total_saidas = 0
    for t in transacoes:
        if t.data.month == mes and t.data.year == ano:
            relatorio.append(f"Data: {t.data.strftime('%d/%m/%Y')}, Tipo: {t.tipo}, Valor: {t.valor:.2f}")
            if t.tipo == "deposito":
                total_entradas += t.valor
            else:
                total_saidas += t.valor

    print("\n--- Relatório Mensal ---")
    for linha in relatorio:
        print(linha)
    print(f"Total de Entradas: {total_entradas:.2f}")
    print(f"Total de Saídas: {total_saidas:.2f}")
    print("------------------------")
    return relatorio

def obter_data_atual():
    # Retorna a data atual
    hoje = datetime.today() # Intencionalmente errado, deveria ser datetime.date.today() ou datetime.datetime.today()
    return hoje

# Exemplo de uso (para testar as funções)
if __name__ == "__main__":
    t1 = Transacao(100.0, "deposito", datetime.date(2026, 5, 10))
    t2 = Transacao(50.0, "saque", datetime.date(2026, 5, 12))
    t3 = Transacao(200.0, "transferencia", datetime.date(2026, 5, 15))
    t4 = Transacao(30.0, "saque", datetime.date(2026, 6, 1))
    t5 = Transacao(150.0, "deposito", datetime.date(2026, 6, 5))

    saldo = 500.0
    limite = 100.0

    print(f"Validando t1: {validar_transacao(t1, saldo, limite)}")
    print(f"Validando t2: {validar_transacao(t2, saldo, limite)}")
    print(f"Validando t3: {validar_transacao(t3, saldo, limite)}")
    print(f"Validando t4: {validar_transacao(t4, saldo, limite)}")
    print(f"Validando t5: {validar_transacao(t5, saldo, limite)}")

    juros = calcular_juros_compostos(1000, 5, 2)
    print(f"Juros compostos: {juros:.2f}")

    todas_transacoes = [t1, t2, t3, t4, t5]
    gerar_relatorio_mensal(todas_transacoes, 5, 2026)
    gerar_relatorio_mensal(todas_transacoes, 6, 2026)

    data_hoje = obter_data_atual()
    print(f"Data atual: {data_hoje}")
    