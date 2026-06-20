# sistema_biblioteca.py
# Sistema de gerenciamento de biblioteca
# Projeto para análise de qualidade - ITMADS537
 
import os
import sys
import math
import datetime
import json
 
livros = []
usuarios = []
emprestimos = []
 
def cadastrarLivro(t, a, i, q):
    l = {}
    l['titulo'] = t
    l['autor'] = a
    l['isbn'] = i
    l['quantidade'] = q
    l['disponivel'] = q
    livros.append(l)
    print("Livro cadastrado: " + t)
 
def cadastrarUsuario(n, e, c):
    u = {}
    u['nome'] = n
    u['email'] = e
    u['cpf'] = c
    u['ativo'] = True
    u['multa'] = 0
    usuarios.append(u)
    print("Usuario cadastrado: " + n)
 
def realizarEmprestimo(cpf, isbn, dias):
    usuario_encontrado = None
    livro_encontrado = None
    for u in usuarios:
        if u['cpf'] == cpf:
            if u['ativo'] == True:
                if u['multa'] > 0:
                    if u['multa'] > 10:
                        print("Usuario bloqueado por multa alta")
                        return False
                    else:
                        print("Usuario com multa pendente mas liberado")
                usuario_encontrado = u
    for l in livros:
        if l['isbn'] == isbn:
            if l['disponivel'] > 0:
                if l['quantidade'] > 0:
                    livro_encontrado = l
            else:
                if l['disponivel'] == 0:
                    print("Livro indisponivel")
                    return False
    if usuario_encontrado == None:
        print("Usuario nao encontrado")
        return False
    if livro_encontrado == None:
        print("Livro nao encontrado")
        return False
    e = {}
    e['cpf'] = cpf
    e['isbn'] = isbn
    e['data_emprestimo'] = str(datetime.date.today())
    e['dias'] = dias
    e['devolvido'] = False
    e['multa_gerada'] = 0
    emprestimos.append(e)
    livro_encontrado['disponivel'] = livro_encontrado['disponivel'] - 1
    print("Emprestimo realizado com sucesso")
    return True
 
def calcularMulta(cpf, isbn):
    multa = 0
    emp = None
    for e in emprestimos:
        if e['cpf'] == cpf:
            if e['isbn'] == isbn:
                if e['devolvido'] == False:
                    emp = e
    if emp == None:
        print("Emprestimo nao encontrado")
        return 0
    data_emp = datetime.datetime.strptime(
        emp['data_emprestimo'], '%Y-%m-%d').date()
    hoje = datetime.date.today()
    delta = hoje - data_emp
    dias_atraso = delta.days - emp['dias']
    if dias_atraso > 0:
        if dias_atraso <= 5:
            multa = dias_atraso * 1.0
        else:
            if dias_atraso <= 15:
                multa = 5 * 1.0 + (dias_atraso - 5) * 2.0
            else:
                if dias_atraso <= 30:
                    multa = 5 * 1.0 + 10 * 2.0 + (dias_atraso - 15) * 3.0
                else:
                    multa = (5 * 1.0 + 10 * 2.0 +
                             15 * 3.0 + (dias_atraso - 30) * 5.0)
    emp['multa_gerada'] = multa
    for u in usuarios:
        if u['cpf'] == cpf:
            u['multa'] = u['multa'] + multa
    return multa
 
def realizarDevolucao(cpf, isbn):
    emp = None
    livro_encontrado = None
    for e in emprestimos:
        if e['cpf'] == cpf:
            if e['isbn'] == isbn:
                if e['devolvido'] == False:
                    emp = e
    if emp == None:
        print("Emprestimo nao encontrado ou ja devolvido")
        return False
    for l in livros:
        if l['isbn'] == isbn:
            livro_encontrado = l
    if livro_encontrado == None:
        print("Livro nao encontrado")
        return False
    multa = calcularMulta(cpf, isbn)
    if multa > 0:
        print("Multa gerada: R$" + str(multa))
    emp['devolvido'] = True
    livro_encontrado['disponivel'] = livro_encontrado['disponivel'] + 1
    print("Devolucao realizada")
    return True
 
def relatorio(x):
    print("=== RELATORIO ===")
    if x == 1:
        print("Livros cadastrados: " + str(len(livros)))
        for l in livros:
            print(l['titulo'] + " - " + l['autor'] +
                  " | Disp: " + str(l['disponivel']) +
                  "/" + str(l['quantidade']))
    if x == 2:
        print("Usuarios cadastrados: " + str(len(usuarios)))
        for u in usuarios:
            status = ""
            if u['ativo'] == True:
                if u['multa'] > 0:
                    status = "ATIVO COM MULTA"
                else:
                    status = "ATIVO"
            else:
                status = "INATIVO"
            print(u['nome'] + " | " + status +
                  " | Multa: R$" + str(u['multa']))
    if x == 3:
        print("Emprestimos ativos:")
        count = 0
        for e in emprestimos:
            if e['devolvido'] == False:
                count = count + 1
                print("CPF: " + e['cpf'] +
                      " | ISBN: " + e['isbn'] +
                      " | Data: " + e['data_emprestimo'])
        print("Total: " + str(count))
 
def verificarDisponibilidade(isbn):
    for l in livros:
        if l['isbn'] == isbn:
            if l['disponivel'] > 0:
                return True
            else:
                return False
    return False
 
def buscarLivro(termo):
    resultado = []
    for l in livros:
        if termo.lower() in l['titulo'].lower():
            resultado.append(l)
        else:
            if termo.lower() in l['autor'].lower():
                resultado.append(l)
    if len(resultado) == 0:
        print("Nenhum resultado encontrado")
    else:
        for r in resultado:
            print(r['titulo'] + " - " + r['autor'])
    return resultado
 
def estatisticas():
    total_livros = len(livros)
    total_usuarios = len(usuarios)
    total_emprestimos = len(emprestimos)
    emprestimos_ativos = 0
    total_multas = 0
    livros_mais_emprestados = {}
    for e in emprestimos:
        if e['devolvido'] == False:
            emprestimos_ativos = emprestimos_ativos + 1
        if e['isbn'] in livros_mais_emprestados:
            livros_mais_emprestados[e['isbn']] = (
                livros_mais_emprestados[e['isbn']] + 1)
        else:
            livros_mais_emprestados[e['isbn']] = 1
    for u in usuarios:
        total_multas = total_multas + u['multa']
    print("Total livros: " + str(total_livros))
    print("Total usuarios: " + str(total_usuarios))
    print("Total emprestimos: " + str(total_emprestimos))
    print("Emprestimos ativos: " + str(emprestimos_ativos))
    print("Total multas pendentes: R$" + str(total_multas))
    if len(livros_mais_emprestados) > 0:
        mais_emprestado = max(livros_mais_emprestados,
                              key=livros_mais_emprestados.get)
        for l in livros:
            if l['isbn'] == mais_emprestado:
                print("Livro mais emprestado: " + l['titulo'])
 
if __name__ == "__main__":
    cadastrarLivro("Clean Code", "Robert Martin",
                   "978-0132350884", 3)
    cadastrarLivro("The Pragmatic Programmer", "David Thomas",
                   "978-0135957059", 2)
    cadastrarLivro("Design Patterns", "Gang of Four",
                   "978-0201633610", 1)
    cadastrarUsuario("Ana Silva", "ana@email.com", "111.111.111-11")
    cadastrarUsuario("Bruno Costa", "bruno@email.com", "222.222.222-22")
    realizarEmprestimo("111.111.111-11", "978-0132350884", 7)
    realizarEmprestimo("222.222.222-22", "978-0135957059", 14)
    relatorio(1)
    relatorio(2)
    relatorio(3)
    estatisticas()
