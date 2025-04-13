import os
import json
import logging
from parser.base_parser import ajustar_regex_dinamicamente

# Diretório onde estão os arquivos de feedback do usuário
FEEDBACK_DIR = "feedbacks"


def carregar_feedbacks():
    feedbacks = []
    for nome_arquivo in os.listdir(FEEDBACK_DIR):
        if nome_arquivo.endswith(".json"):
            caminho = os.path.join(FEEDBACK_DIR, nome_arquivo)
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    feedbacks.append(dados)
            except Exception as e:
                logging.warning(f"Erro ao ler feedback {nome_arquivo}: {e}")
    return feedbacks


def extrair_exemplos_para_aprendizado(feedbacks):
    exemplos = []
    for item in feedbacks:
        for promo in item:
            if promo.get("status") == "ajustar":
                exemplos.append(promo)
    return exemplos


def aplicar_aprendizado_incremental():
    feedbacks = carregar_feedbacks()
    exemplos = extrair_exemplos_para_aprendizado(feedbacks)

    if not exemplos:
        logging.info("Nenhum feedback com status 'ajustar' encontrado.")
        return

    logging.info(f"🔄 Ajustando parser com {len(exemplos)} exemplos corrigidos...")
    ajustar_regex_dinamicamente(exemplos)
    logging.info("✅ Ajustes aplicados com sucesso!")


if __name__ == "__main__":
    aplicar_aprendizado_incremental()