import json
from difflib import SequenceMatcher

from app_paths import DATASET_DIR, ensure_runtime_dirs
from parser.base_parser import extrair_promocoes


ensure_runtime_dirs()


def similaridade(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def aprender_com_dataset(threshold: float = 0.7) -> dict:
    arquivos = sorted(DATASET_DIR.glob("*.json"))
    total = 0
    ajustaveis = 0

    for caminho in arquivos:
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        entradas_ocr = dados.get("entradas_ocr", [])
        resultados_parser = dados.get("resultados_parser", [])
        if not entradas_ocr or not resultados_parser:
            continue

        resultado_antigo = resultados_parser[0] if isinstance(resultados_parser[0], list) else []
        novo_resultado = extrair_promocoes(entradas_ocr[0])

        for novo in novo_resultado:
            if not any(
                similaridade(novo["produto"], antigo.get("produto", "")) >= threshold
                for antigo in resultado_antigo
            ):
                ajustaveis += 1
        total += len(novo_resultado)

    precisao = round(100 * (total - ajustaveis) / total, 2) if total else 0.0
    return {
        "total_produtos_analisados": total,
        "produtos_com_baixa_similaridade": ajustaveis,
        "precisao": precisao,
    }


if __name__ == "__main__":
    print(json.dumps(aprender_com_dataset(), indent=2, ensure_ascii=False))
