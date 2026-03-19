import json
import re
from datetime import datetime, timezone

from app_paths import LEARNING_RULES_PATH


DEFAULT_IGNORE_TERMS = {
    "cada",
    "g",
    "kg",
    "ml",
    "l",
    "un",
    "tp",
    "pet",
    "frasco",
    "garrafa",
    "r$",
    "leve",
    "pague",
    "pague menos",
    "mais",
    "promo",
    "oferta",
    "com",
}
DEFAULT_CONDITION_MARKERS = {
    "A PARTIR DE",
    "NA COMPRA DE",
    "LEVANDO",
    "ACIMA DE",
    "CADA",
}

PRICE_PATTERN = re.compile(r"R\$ ?\d{1,3}(?:[.,]\d{2})", re.IGNORECASE)
PRICE_REMOVAL_PATTERN = re.compile(r"R\$ ?\d+[,\.]?\d*", re.IGNORECASE)
PUNCTUATION_PATTERN = re.compile(r"[^\w\sÀ-ÿ]")
MULTISPACE_PATTERN = re.compile(r"\s+")


def _default_learning_rules() -> dict:
    return {
        "ignore_terms": sorted(DEFAULT_IGNORE_TERMS),
        "condition_markers": sorted(DEFAULT_CONDITION_MARKERS),
        "reviewed_examples": 0,
        "updated_at": None,
    }


def _load_learning_rules() -> dict:
    if not LEARNING_RULES_PATH.exists():
        return _default_learning_rules()

    try:
        data = json.loads(LEARNING_RULES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _default_learning_rules()

    return {
        "ignore_terms": sorted(set(data.get("ignore_terms", [])) | DEFAULT_IGNORE_TERMS),
        "condition_markers": sorted(set(data.get("condition_markers", [])) | DEFAULT_CONDITION_MARKERS),
        "reviewed_examples": int(data.get("reviewed_examples", 0)),
        "updated_at": data.get("updated_at"),
    }


def limpar_nome_produto(nome: str, ignore_terms: set[str] | None = None) -> str:
    termos_ignorados = ignore_terms or DEFAULT_IGNORE_TERMS
    nome = PRICE_REMOVAL_PATTERN.sub("", nome)
    nome = re.sub(r"\b(?:%s)\b" % "|".join(re.escape(termo) for termo in termos_ignorados), "", nome, flags=re.IGNORECASE)
    nome = PUNCTUATION_PATTERN.sub("", nome)
    nome = MULTISPACE_PATTERN.sub(" ", nome).strip()
    return nome.title()


def _extrair_nome_produto(linhas: list[str], index_preco: int, ignore_terms: set[str]) -> str:
    nome_linhas: list[str] = []
    for offset in range(1, 4):
        index_linha = index_preco - offset
        if index_linha < 0:
            break
        linha_acima = linhas[index_linha].strip()
        if linha_acima and not PRICE_PATTERN.search(linha_acima):
            nome_linhas.insert(0, linha_acima)
    return limpar_nome_produto(" ".join(nome_linhas), ignore_terms)


def _extrair_condicao(linhas: list[str], index_preco: int, condition_markers: set[str]) -> str:
    for offset in range(1, 3):
        index_linha = index_preco + offset
        if index_linha >= len(linhas):
            break
        linha = linhas[index_linha].strip()
        linha_upper = linha.upper()
        if any(marker in linha_upper for marker in condition_markers):
            return linha
    return ""


def extrair_promocoes(texto: str) -> list[dict]:
    rules = _load_learning_rules()
    ignore_terms = set(rules["ignore_terms"])
    condition_markers = set(rules["condition_markers"])

    promocoes: list[dict] = []
    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]

    for i, linha in enumerate(linhas):
        precos = PRICE_PATTERN.findall(linha)
        if not precos:
            continue

        preco_promocional = precos[-1]
        preco_original = precos[0] if len(precos) > 1 and precos[0] != preco_promocional else None
        nome_completo = _extrair_nome_produto(linhas, i, ignore_terms)
        condicao = _extrair_condicao(linhas, i, condition_markers)

        if nome_completo and len(nome_completo.split()) >= 2:
            promocoes.append(
                {
                    "produto": nome_completo,
                    "preco_original": preco_original,
                    "preco_promocional": preco_promocional,
                    "condicao": condicao,
                }
            )

    return promocoes


def ajustar_regex_dinamicamente(exemplos: list[dict]) -> dict:
    rules = _load_learning_rules()
    condition_markers = set(rules["condition_markers"])

    for exemplo in exemplos:
        condicao = (exemplo.get("condicao") or "").strip()
        if condicao:
            condition_markers.add(condicao.upper())

    updated_rules = {
        "ignore_terms": rules["ignore_terms"],
        "condition_markers": sorted(condition_markers),
        "reviewed_examples": rules["reviewed_examples"] + len(exemplos),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    LEARNING_RULES_PATH.write_text(json.dumps(updated_rules, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "examples_processed": len(exemplos),
        "condition_markers": len(updated_rules["condition_markers"]),
        "rules_path": str(LEARNING_RULES_PATH),
    }
