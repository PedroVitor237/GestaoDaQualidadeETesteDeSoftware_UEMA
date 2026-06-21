import datetime
from unittest.mock import patch

import pytest

from validador_cadastro import ValidadorCadastro, TipoUsuario, StatusCadastro


@pytest.fixture
def validador():
    return ValidadorCadastro()


def test_validar_senha_forte(validador):
    assert validador.validar_senha("Senha123") is True


def test_validar_senha_fraca(validador):
    assert validador.validar_senha("senha") is False


def test_cadastrar_usuario_envia_sms_com_mock(validador):
    with patch.object(validador.sms, "enviar_confirmacao") as mock_sms:
        # TODO: cadastre um usuário válido e verifique chamada do SMS.
        pass