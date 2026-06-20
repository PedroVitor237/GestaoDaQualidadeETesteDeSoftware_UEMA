"""
PASSO 2 - Primeiro teste: comportamento de criação de tarefa
Crie o arquivo test_tarefas.py. Comece por um teste simples para uma entrada válida e depois escolha pelo menos duas entradas que deveriam ser tratadas com cuidado.
"""


# test_tarefas.py
import pytest
from unittest.mock import patch
from sistema_tarefas import SistemaGestaoTarefas, Prioridade, Status

@pytest.fixture
def sistema():
    with patch('sistema_tarefas.NotificadorEmail'):
        yield SistemaGestaoTarefas()

def test_criar_tarefa_com_dados_validos(sistema):
    tarefa_id = sistema.criar_tarefa('Implementar login')
    assert tarefa_id is not None
    assert sistema.tarefas[tarefa_id]['titulo'] == 'Implementar login'

def test_criar_tarefa_com_entrada_invalida(sistema):
    # TODO: escolha uma entrada inválida e defina o comportamento esperado.
    # Exemplo de decisão: rejeitar, normalizar, lançar exceção ou registrar erro.
    pass


# Dê nomes claros aos testes e justifique tecnicamente qualquer comportamento que pareça arriscado.