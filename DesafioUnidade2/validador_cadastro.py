"""
validador_cadastro.py — Sistema da 2ª Avaliação Prática
ITMADS537 | Gestão da Qualidade e Teste de Software — Unidade 2
Sábado 21/06/2026

PRIMEIRO escreva testes. Depois documente qualquer correção realizada.

Sua tarefa: escrever a suite de testes em test_validador.py

Metas obrigatórias:
  - Cobertura >= 70% com coverage.py
  - Pelo menos 1 mock com unittest.mock
  - relatorio_testes.html gerado sem erros de execução

Executar:
pytest test_validador.py -v


  pytest test_validador.py -v
      --html=relatorio_testes.html
      --self-contained-html

  coverage run -m pytest test_validador.py -v
  coverage report -m
  coverage html -d htmlcov/
"""

import re
import datetime
from enum import Enum


# ── Enumerações ──────────────────────────────────────────────────────────────

class TipoUsuario(Enum):
    ESTUDANTE = "estudante"
    PROFESSOR = "professor"
    ADMIN     = "admin"


class StatusCadastro(Enum):
    ATIVO     = "ativo"
    INATIVO   = "inativo"
    BLOQUEADO = "bloqueado"
    PENDENTE  = "pendente"


# ── Serviço externo (deve ser mockado nos testes) ────────────────────────────

class ServicoNotificacaoSMS:
    """
    Envia SMS de confirmação de cadastro.
    Dependência externa — deve ser mockada nos testes.
    """

    def enviar_confirmacao(self, telefone, codigo):
        print(f"[SMS] Enviando código {codigo} para {telefone}")
        return {"status": "enviado", "telefone": telefone}

    def enviar_boas_vindas(self, telefone, nome):
        print(f"[SMS] Bem-vindo, {nome}! Cadastro realizado.")
        return {"status": "enviado", "telefone": telefone}


# ── Validador principal ──────────────────────────────────────────────────────

class ValidadorCadastro:
    """
    Valida e registra cadastros de usuários do sistema acadêmico.

    A implementação deve ser analisada por meio de testes automatizados.
    Use os requisitos do enunciado para definir comportamentos esperados,
    casos válidos, casos inválidos e cenários de regressão.
    """

    CPF_INVALIDOS_CONHECIDOS = [
        "00000000000", "11111111111", "22222222222",
        "33333333333", "44444444444", "55555555555",
        "66666666666", "77777777777", "88888888888",
        "99999999099",
    ]

    def __init__(self):
        self.usuarios    = {}
        self._proximo_id = 1
        self.sms         = ServicoNotificacaoSMS()

    # ── Validações individuais ───────────────────────────────────────────────

    def validar_cpf(self, cpf):
        """Valida o CPF informado, considerando formato e regras de aceitação."""
        if not isinstance(cpf, str):
            return False
        cpf_limpo = cpf.replace(".", "").replace("-", "")
        if len(cpf_limpo) != 11:
            return False
        if not cpf_limpo.isdigit():
            return False
        if cpf_limpo in self.CPF_INVALIDOS_CONHECIDOS:
            return False

    def validar_email(self, email, tipo_usuario=None):
        """Valida o e-mail informado, considerando formato e tipo de usuário."""
        if not isinstance(email, str):
            return False
        if not email.strip():
            return False
        padrao = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
        if not re.match(padrao, email):
            return False
        return True

    def validar_senha(self, senha):
        """
        Valida força da senha.
        Regras: mínimo 8 caracteres, pelo menos 1 número, pelo menos 1 maiúscula.
        """
        if not isinstance(senha, str):
            return False
        if len(senha) < 8:
            return False
        if not any(c.isdigit() for c in senha):
            return False
        if not any(c.isupper() for c in senha):
            return False
        return True

    def validar_telefone(self, telefone):
        """Valida formato de telefone brasileiro."""
        if not isinstance(telefone, str):
            return False
        tel_limpo = (telefone
                     .replace("(", "")
                     .replace(")", "")
                     .replace("-", "")
                     .replace(" ", ""))
        if len(tel_limpo) not in [10, 11]:
            return False
        if not tel_limpo.isdigit():
            return False
        return True

    def validar_data_nascimento(self, data_nascimento, tipo_usuario=None):
        """Valida a data de nascimento de acordo com as regras de cadastro."""
        if not isinstance(data_nascimento, datetime.date):
            return False
        hoje = datetime.date.today()
        if data_nascimento >= hoje:
            return False
        idade = (hoje - data_nascimento).days // 365
        if idade > 120:
            return False
        return True

    # ── Cadastro ─────────────────────────────────────────────────────────────

    def cadastrar_usuario(self, nome, cpf, email, senha, telefone,
                          data_nascimento, tipo=TipoUsuario.ESTUDANTE):
        """
        Realiza o cadastro completo de um usuário.

        Retorna dict com id e status, ou lança ValueError se inválido.
        """
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("Nome é obrigatório e não pode estar vazio")
        if len(nome.strip()) < 3:
            raise ValueError("Nome deve ter pelo menos 3 caracteres")

        if not self.validar_cpf(cpf):
            raise ValueError(f"CPF inválido: {cpf}")

        for u in self.usuarios.values():
            if u["cpf"] == cpf.replace(".", "").replace("-", ""):
                raise ValueError("CPF já cadastrado no sistema")

        if not self.validar_email(email, tipo):
            raise ValueError(f"E-mail inválido: {email}")

        if not self.validar_senha(senha):
            raise ValueError(
                "Senha deve ter mínimo 8 caracteres, "
                "1 número e 1 letra maiúscula"
            )

        if not self.validar_telefone(telefone):
            raise ValueError(f"Telefone inválido: {telefone}")

        if not self.validar_data_nascimento(data_nascimento, tipo):
            raise ValueError("Data de nascimento inválida")

        codigo = self._gerar_codigo_confirmacao(cpf)

        usuario_id = self._proximo_id
        self._proximo_id += 1

        usuario = {
            "id":                 usuario_id,
            "nome":               nome.strip(),
            "cpf":                cpf.replace(".", "").replace("-", ""),
            "email":              email.lower().strip(),
            "telefone":           telefone,
            "data_nascimento":    data_nascimento,
            "tipo":               tipo,
            "status":             StatusCadastro.PENDENTE,
            "cadastrado_em":      datetime.datetime.now(),
            "codigo_confirmacao": codigo,
        }

        self.usuarios[usuario_id] = usuario

        # Chama serviço externo — deve ser mockado nos testes
        self.sms.enviar_confirmacao(telefone, codigo)

        return {"id": usuario_id, "status": "pendente", "codigo": codigo}

    def confirmar_cadastro(self, usuario_id, codigo_informado):
        """
        Confirma o cadastro validando o código SMS.
        Ativa o usuário e envia SMS de boas-vindas.
        """
        if usuario_id not in self.usuarios:
            raise ValueError(f"Usuário {usuario_id} não encontrado")

        usuario = self.usuarios[usuario_id]

        if usuario["status"] != StatusCadastro.PENDENTE:
            raise ValueError("Cadastro não está pendente de confirmação")

        if usuario["codigo_confirmacao"] != codigo_informado:
            raise ValueError("Código de confirmação incorreto")

        usuario["status"] = StatusCadastro.ATIVO

        # Chama serviço externo — deve ser mockado nos testes
        self.sms.enviar_boas_vindas(usuario["telefone"], usuario["nome"])

        return True

    # ── Mensalidade ──────────────────────────────────────────────────────────

    def calcular_mensalidade(self, usuario_id):
        """Calcula mensalidade com base no tipo de usuário e condições especiais."""
        if usuario_id not in self.usuarios:
            raise ValueError(f"Usuário {usuario_id} não encontrado")

        usuario = self.usuarios[usuario_id]
        tipo    = usuario["tipo"]

        if tipo == TipoUsuario.ESTUDANTE:
            valor_base = 250.00
        elif tipo == TipoUsuario.PROFESSOR:
            valor_base = 0.00
        elif tipo == TipoUsuario.ADMIN:
            valor_base = 0.00
        else:
            valor_base = 250.00

        hoje  = datetime.date.today()
        idade = (hoje - usuario["data_nascimento"]).days // 365

        desconto_idade = 0.0
        if tipo == TipoUsuario.ESTUDANTE:
            if idade < 18:
                desconto_idade = 0.20
            elif idade >= 60:
                desconto_idade = 0.15

        desconto_especial = 0.0
        if tipo == TipoUsuario.ADMIN:
            desconto_especial = 1.0

        if usuario["status"] == StatusCadastro.BLOQUEADO:
            return 0.00
        if usuario["status"] == StatusCadastro.INATIVO:
            return valor_base * 0.50

        desconto_total = desconto_idade + desconto_especial
        if desconto_total > 1.0:
            desconto_total = 1.0

        valor_final = valor_base * (1 - desconto_total)
        return round(valor_final, 2)

    # ── Consultas ────────────────────────────────────────────────────────────

    def buscar_usuario(self, usuario_id):
        """Retorna um usuário pelo ID."""
        if usuario_id not in self.usuarios:
            raise ValueError(f"Usuário {usuario_id} não encontrado")
        return self.usuarios[usuario_id]

    def listar_por_tipo(self, tipo):
        """Lista todos os usuários de um determinado tipo."""
        return [u for u in self.usuarios.values() if u["tipo"] == tipo]

    def listar_por_status(self, status):
        """Lista todos os usuários com um determinado status."""
        return [u for u in self.usuarios.values() if u["status"] == status]

    def contar_por_tipo(self):
        """Retorna contagem de usuários agrupados por tipo."""
        contagem = {tipo: 0 for tipo in TipoUsuario}
        for u in self.usuarios.values():
            contagem[u["tipo"]] += 1
        return contagem

    # ── Arquivamento ─────────────────────────────────────────────────────────

    def arquivar_usuario(self, usuario_id):
        """Arquiva ou inativa um usuário de acordo com as regras do sistema."""
        if usuario_id not in self.usuarios:
            raise ValueError(f"Usuário {usuario_id} não encontrado")

        usuario = self.usuarios[usuario_id]
        usuario["status"] = StatusCadastro.INATIVO
        return True

    # ── Auxiliares ───────────────────────────────────────────────────────────

    def _gerar_codigo_confirmacao(self, cpf):
        """Gera código de confirmação baseado no CPF."""
        cpf_limpo = cpf.replace(".", "").replace("-", "")
        return str(sum(int(d) for d in cpf_limpo) % 9000 + 1000)
