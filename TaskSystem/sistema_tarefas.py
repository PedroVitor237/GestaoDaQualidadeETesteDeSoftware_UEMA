"""
Sistema de Gestão de Tarefas — ITMADS537 / Unidade 2
Laboratório prático: pytest, coverage.py, unittest.mock

PROBLEMAS PROPOSITAIS (não corrigir antes da aula):
  1. Caixa-preta: validações de entrada ausentes ou incorretas
  2. Caixa-branca: função calcular_prioridade_final com CC alta (radon deve marcar C ou D)
  3. Mocks: notificador chamado diretamente sem injeção de dependência
  4. Cobertura: branch de urgência crítica sem cobertura
  5. Regressão: função arquivar_tarefa não tem testes
"""

import json
import datetime
from enum import Enum


class Prioridade(Enum):
    BAIXA   = 1
    MEDIA   = 2
    ALTA    = 3
    URGENTE = 4


class Status(Enum):
    PENDENTE   = "pendente"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA  = "concluida"
    ARQUIVADA  = "arquivada"


# ── Notificador externo (dependência que deve ser mockada nos testes) ────────
class NotificadorEmail:
    """Envia e-mails de notificação. Dependência externa — deve ser mockada."""

    def notificar_criacao(self, tarefa):
        # Simula chamada a serviço externo de e-mail
        print(f"[EMAIL] Nova tarefa criada: {tarefa['titulo']}")
        return True

    def notificar_conclusao(self, tarefa):
        print(f"[EMAIL] Tarefa concluída: {tarefa['titulo']}")
        return True

    def notificar_atraso(self, tarefa, dias_atraso):
        print(f"[EMAIL] Tarefa atrasada {dias_atraso} dias: {tarefa['titulo']}")
        return True


# ── Sistema principal ────────────────────────────────────────────────────────
class SistemaGestaoTarefas:

    def __init__(self):
        self.tarefas = {}
        self._proximo_id = 1
        self.notificador = NotificadorEmail()  # PROBLEMA: dependência hard-coded

    # ── Criação ─────────────────────────────────────────────────────────────

    def criar_tarefa(self, titulo, descricao="", prioridade=Prioridade.MEDIA,
                     prazo=None, responsavel=None):
        """
        Cria uma nova tarefa no sistema.

        PROBLEMAS PROPOSITAIS para teste caixa-preta:
          - titulo vazio não é validado → permite tarefa sem nome
          - prioridade não é validada → aceita string, int, qualquer coisa
          - prazo no passado não é validado → permite prazo já vencido
          - responsavel com e-mail inválido não é validado
        """
        tarefa_id = self._proximo_id
        self._proximo_id += 1

        tarefa = {
            "id":          tarefa_id,
            "titulo":      titulo,          # BUG: aceita string vazia
            "descricao":   descricao,
            "prioridade":  prioridade,      # BUG: não valida tipo
            "status":      Status.PENDENTE,
            "prazo":       prazo,           # BUG: aceita datas no passado
            "responsavel": responsavel,     # BUG: não valida formato de e-mail
            "criado_em":   datetime.datetime.now(),
            "concluido_em": None,
            "subtarefas":  [],
            "tags":        [],
        }

        self.tarefas[tarefa_id] = tarefa
        self.notificador.notificar_criacao(tarefa)  # PROBLEMA: chama diretamente
        return tarefa_id

    # ── Atualização ──────────────────────────────────────────────────────────

    def atualizar_status(self, tarefa_id, novo_status):
        """Atualiza o status de uma tarefa."""
        if tarefa_id not in self.tarefas:
            raise ValueError(f"Tarefa {tarefa_id} não encontrada")

        tarefa = self.tarefas[tarefa_id]

        # BUG: não valida transições de status
        # Deveria impedir: CONCLUIDA → PENDENTE, ARQUIVADA → qualquer coisa
        tarefa["status"] = novo_status

        if novo_status == Status.CONCLUIDA:
            tarefa["concluido_em"] = datetime.datetime.now()
            self.notificador.notificar_conclusao(tarefa)

        return True

    def adicionar_subtarefa(self, tarefa_pai_id, titulo_subtarefa):
        """Adiciona uma subtarefa a uma tarefa existente."""
        if tarefa_pai_id not in self.tarefas:
            raise ValueError(f"Tarefa {tarefa_pai_id} não encontrada")

        # BUG: não valida se título da subtarefa está vazio
        # BUG: não limita quantidade de subtarefas
        self.tarefas[tarefa_pai_id]["subtarefas"].append({
            "titulo": titulo_subtarefa,
            "concluida": False
        })
        return True

    def adicionar_tag(self, tarefa_id, tag):
        """Adiciona uma tag a uma tarefa."""
        if tarefa_id not in self.tarefas:
            raise ValueError(f"Tarefa {tarefa_id} não encontrada")
        # BUG: não normaliza a tag (maiúsculas/minúsculas)
        # BUG: permite tags duplicadas
        self.tarefas[tarefa_id]["tags"].append(tag)
        return True

    # ── Prioridade ───────────────────────────────────────────────────────────

    def calcular_prioridade_final(self, tarefa_id):
        """
        Calcula a prioridade final considerando prazo, subtarefas e tags especiais.

        PROBLEMA: complexidade ciclomática alta (CC esperado: D ou C pelo radon).
        Esta função é propositalmente complexa para o exercício de refatoração.
        """
        if tarefa_id not in self.tarefas:
            raise ValueError(f"Tarefa {tarefa_id} não encontrada")

        tarefa = self.tarefas[tarefa_id]
        score = tarefa["prioridade"].value  # 1–4

        # Fator 1: prazo
        if tarefa["prazo"] is not None:
            hoje = datetime.date.today()
            dias_restantes = (tarefa["prazo"] - hoje).days
            if dias_restantes < 0:
                score += 4  # atrasada
            elif dias_restantes == 0:
                score += 3  # vence hoje
            elif dias_restantes <= 2:
                score += 2  # vence em 2 dias
            elif dias_restantes <= 7:
                score += 1  # vence em 1 semana

        # Fator 2: subtarefas pendentes
        subtarefas_pendentes = sum(
            1 for s in tarefa["subtarefas"] if not s["concluida"]
        )
        if subtarefas_pendentes > 5:
            score += 2
        elif subtarefas_pendentes > 2:
            score += 1

        # Fator 3: tags especiais
        tags = [t.lower() for t in tarefa["tags"]]
        if "critico" in tags or "critica" in tags:
            score += 3
        if "bloqueio" in tags:
            score += 2
        if "cliente" in tags:
            score += 1
        if "interno" in tags:
            score -= 1  # prioridade menor para tarefas internas

        # Fator 4: status
        if tarefa["status"] == Status.EM_ANDAMENTO:
            score += 1  # em andamento tem prioridade ligeiramente maior

        # PROBLEMA: branch de urgência crítica sem cobertura nos testes
        # (score > 10 nunca é alcançado nos testes básicos)
        if score > 10:
            # Situação de emergência: notificar imediatamente
            self.notificador.notificar_atraso(tarefa, abs(
                (tarefa["prazo"] - datetime.date.today()).days
                if tarefa["prazo"] else 0
            ))
            return "URGENCIA_CRITICA"

        # Normaliza score para categorias
        if score >= 8:
            return Prioridade.URGENTE
        elif score >= 6:
            return Prioridade.ALTA
        elif score >= 4:
            return Prioridade.MEDIA
        else:
            return Prioridade.BAIXA

    # ── Consulta ─────────────────────────────────────────────────────────────

    def listar_tarefas(self, status=None, prioridade=None, responsavel=None):
        """Lista tarefas com filtros opcionais."""
        resultado = list(self.tarefas.values())

        if status is not None:
            resultado = [t for t in resultado if t["status"] == status]
        if prioridade is not None:
            resultado = [t for t in resultado if t["prioridade"] == prioridade]
        if responsavel is not None:
            resultado = [t for t in resultado if t["responsavel"] == responsavel]

        return resultado

    def buscar_por_tag(self, tag):
        """Busca tarefas por tag."""
        # BUG: busca case-sensitive — 'Critico' não encontra 'critico'
        return [t for t in self.tarefas.values() if tag in t["tags"]]

    def contar_tarefas_por_status(self):
        """Retorna contagem de tarefas agrupadas por status."""
        contagem = {status: 0 for status in Status}
        for tarefa in self.tarefas.values():
            contagem[tarefa["status"]] += 1
        return contagem

    # ── Arquivamento ─────────────────────────────────────────────────────────

    def arquivar_tarefa(self, tarefa_id):
        """
        Arquiva uma tarefa concluída.
        PROBLEMA: função sem nenhum teste na suite — candidata a teste de regressão.
        """
        if tarefa_id not in self.tarefas:
            raise ValueError(f"Tarefa {tarefa_id} não encontrada")

        tarefa = self.tarefas[tarefa_id]

        # BUG: permite arquivar tarefas que não estão concluídas
        # Deveria exigir: status == CONCLUIDA antes de arquivar
        tarefa["status"] = Status.ARQUIVADA
        return True

    # ── Exportação ───────────────────────────────────────────────────────────

    def exportar_json(self):
        """Exporta todas as tarefas em formato JSON."""
        dados = []
        for tarefa in self.tarefas.values():
            dados.append({
                "id":          tarefa["id"],
                "titulo":      tarefa["titulo"],
                "prioridade":  tarefa["prioridade"].name,
                "status":      tarefa["status"].value,
                "responsavel": tarefa["responsavel"],
                "prazo":       str(tarefa["prazo"]) if tarefa["prazo"] else None,
                "tags":        tarefa["tags"],
                "subtarefas":  len(tarefa["subtarefas"]),
            })
        return json.dumps(dados, ensure_ascii=False, indent=2)
