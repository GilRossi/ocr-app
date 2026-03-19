import datetime
import hashlib
import json

from google.cloud import vision

from app_paths import DATASET_DIR, ensure_runtime_dirs
from .base_parser import extrair_promocoes


ensure_runtime_dirs()


def gerar_hash(conteudo_bytes: bytes) -> str:
    return hashlib.sha256(conteudo_bytes).hexdigest()[:12]


def processar_imagem_vision(
    client: vision.ImageAnnotatorClient,
    imagem_bytes: bytes,
    execucoes: int = 1,
) -> dict:
    hash_imagem = gerar_hash(imagem_bytes)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    resultados_ocr: list[str] = []
    resultados_parser: list[list[dict] | dict] = []

    for _ in range(execucoes):
        response = client.text_detection(image=vision.Image(content=imagem_bytes))
        textos = response.text_annotations
        if not textos:
            continue

        texto_ocr = textos[0].description
        resultados_ocr.append(texto_ocr)
        try:
            resultados_parser.append(extrair_promocoes(texto_ocr))
        except Exception as exc:
            resultados_parser.append({"erro": str(exc)})

    resultado_final = {
        "imagem_hash": hash_imagem,
        "timestamp": timestamp,
        "quantidade_execucoes": execucoes,
        "entradas_ocr": resultados_ocr,
        "resultados_parser": resultados_parser,
    }

    caminho_arquivo = DATASET_DIR / f"{timestamp}_{hash_imagem}.json"
    caminho_arquivo.write_text(json.dumps(resultado_final, indent=2, ensure_ascii=False), encoding="utf-8")
    return resultado_final
