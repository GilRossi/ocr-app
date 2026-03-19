import json
import logging

from app_paths import FEEDBACK_DIR, ensure_runtime_dirs
from parser.base_parser import ajustar_regex_dinamicamente


logger = logging.getLogger(__name__)
ensure_runtime_dirs()


def carregar_feedbacks() -> list[list[dict]]:
    feedbacks: list[list[dict]] = []
    for arquivo in FEEDBACK_DIR.glob("*.json"):
        try:
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
            if isinstance(dados, list):
                feedbacks.append(dados)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Erro ao ler feedback %s: %s", arquivo.name, exc)
    return feedbacks


def extrair_exemplos_para_aprendizado(feedbacks: list[list[dict]]) -> list[dict]:
    exemplos: list[dict] = []
    for grupo in feedbacks:
        for promo in grupo:
            if promo.get("status") == "ajustar":
                exemplos.append(promo)
    return exemplos


def aplicar_aprendizado_incremental() -> dict:
    feedbacks = carregar_feedbacks()
    exemplos = extrair_exemplos_para_aprendizado(feedbacks)

    if not exemplos:
        logger.info("Nenhum feedback com status 'ajustar' encontrado.")
        return {"examples_processed": 0, "message": "Nenhum feedback pendente de ajuste."}

    logger.info("Ajustando parser com %s exemplos corrigidos", len(exemplos))
    resumo = ajustar_regex_dinamicamente(exemplos)
    logger.info("Ajustes aplicados com sucesso")
    return resumo


if __name__ == "__main__":
    print(json.dumps(aplicar_aprendizado_incremental(), indent=2, ensure_ascii=False))
