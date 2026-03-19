import hashlib
import json
from datetime import datetime
from pathlib import Path

from google.cloud import vision

from app_paths import DATASET_DIR, OCR_RESULTS_DIR, OCR_TEXT_DIR, ensure_runtime_dirs
from parser.base_parser import extrair_promocoes


IMAGENS_DIR = DATASET_DIR / "imagens"

ensure_runtime_dirs()


def gerar_hash(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()[:12]


def get_vision_client() -> vision.ImageAnnotatorClient:
    return vision.ImageAnnotatorClient()


def processar_imagem(caminho_imagem: Path) -> dict:
    imagem_bytes = caminho_imagem.read_bytes()
    hash_img = gerar_hash(imagem_bytes)
    nome_base = caminho_imagem.stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    response = get_vision_client().text_detection(image=vision.Image(content=imagem_bytes))
    textos = response.text_annotations
    texto_ocr = textos[0].description if textos else ""

    caminho_ocr = OCR_TEXT_DIR / f"{timestamp}_{hash_img}_{nome_base}.txt"
    caminho_ocr.write_text(texto_ocr, encoding="utf-8")

    try:
        promocoes = extrair_promocoes(texto_ocr)
    except Exception as exc:
        promocoes = [{"erro": str(exc)}]

    resultado = {
        "arquivo": nome_base,
        "imagem_hash": hash_img,
        "timestamp": timestamp,
        "texto_ocr": texto_ocr,
        "promocoes": promocoes,
    }

    caminho_resultado = OCR_RESULTS_DIR / f"{timestamp}_{hash_img}_{nome_base}.json"
    caminho_resultado.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    return resultado


def rodar_pipeline() -> None:
    imagens = sorted(
        caminho for caminho in IMAGENS_DIR.glob("*") if caminho.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )

    if not imagens:
        print("Nenhuma imagem encontrada em 'dataset/imagens'.")
        return

    for imagem in imagens:
        resultado = processar_imagem(imagem)
        print(f"Processado: {resultado['arquivo']} | {len(resultado['promocoes'])} promoções encontradas.")


if __name__ == "__main__":
    rodar_pipeline()
