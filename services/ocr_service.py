import hashlib
import json
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from google.cloud import vision

from app_paths import DATASET_DIR, ensure_runtime_dirs
from parser.base_parser import extrair_promocoes
from settings import Settings


def gerar_hash(conteudo_bytes: bytes) -> str:
    return hashlib.sha256(conteudo_bytes).hexdigest()[:12]


def _salvar_resultado(resultado: dict) -> Path:
    ensure_runtime_dirs()
    caminho_arquivo = DATASET_DIR / f"{resultado['timestamp']}_{resultado['imagem_hash']}.json"
    caminho_arquivo.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    return caminho_arquivo


@lru_cache(maxsize=1)
def _get_google_client() -> vision.ImageAnnotatorClient:
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise RuntimeError("A variável GOOGLE_APPLICATION_CREDENTIALS não foi definida.")
    if not Path(credentials_path).exists():
        raise RuntimeError("O arquivo de credenciais configurado não existe.")
    return vision.ImageAnnotatorClient()


def _executar_ocr_google(imagem_bytes: bytes, execucoes: int) -> list[str]:
    client = _get_google_client()
    resultados: list[str] = []

    for _ in range(execucoes):
        response = client.text_detection(image=vision.Image(content=imagem_bytes))
        textos = response.text_annotations
        resultados.append(textos[0].description if textos else "")

    return resultados


def _executar_ocr_mock(settings: Settings, execucoes: int) -> list[str]:
    return [settings.mock_ocr_text for _ in range(execucoes)]


def processar_ocr(imagem_bytes: bytes, execucoes: int, settings: Settings) -> dict:
    if settings.ocr_provider == "mock":
        entradas_ocr = _executar_ocr_mock(settings, execucoes)
    elif settings.ocr_provider == "google":
        entradas_ocr = _executar_ocr_google(imagem_bytes, execucoes)
    else:
        raise ValueError("OCR_PROVIDER inválido. Use 'mock' ou 'google'.")

    resultados_parser: list[list[dict] | dict] = []
    for texto_ocr in entradas_ocr:
        try:
            resultados_parser.append(extrair_promocoes(texto_ocr))
        except Exception as exc:
            resultados_parser.append({"erro": str(exc)})

    resultado = {
        "imagem_hash": gerar_hash(imagem_bytes),
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "quantidade_execucoes": execucoes,
        "ocr_provider": settings.ocr_provider,
        "entradas_ocr": entradas_ocr,
        "resultados_parser": resultados_parser,
    }
    caminho_arquivo = _salvar_resultado(resultado)
    resultado["arquivo_resultado"] = str(caminho_arquivo)
    return resultado
