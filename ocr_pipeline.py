import json
from datetime import datetime
from pathlib import Path

from app_paths import DATASET_DIR, OCR_RESULTS_DIR, OCR_TEXT_DIR, ensure_runtime_dirs
from services.ocr_service import processar_ocr
from settings import load_settings


IMAGENS_DIR = DATASET_DIR / "imagens"
settings = load_settings()

ensure_runtime_dirs()


def processar_imagem(caminho_imagem: Path) -> dict:
    imagem_bytes = caminho_imagem.read_bytes()
    nome_base = caminho_imagem.stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    resultado_ocr = processar_ocr(imagem_bytes, execucoes=1, settings=settings)
    texto_ocr = resultado_ocr["entradas_ocr"][0] if resultado_ocr["entradas_ocr"] else ""

    caminho_ocr = OCR_TEXT_DIR / f"{timestamp}_{resultado_ocr['imagem_hash']}_{nome_base}.txt"
    caminho_ocr.write_text(texto_ocr, encoding="utf-8")

    resultado = {
        "arquivo": nome_base,
        "imagem_hash": resultado_ocr["imagem_hash"],
        "timestamp": timestamp,
        "ocr_provider": resultado_ocr["ocr_provider"],
        "texto_ocr": texto_ocr,
        "promocoes": resultado_ocr["resultados_parser"][0] if resultado_ocr["resultados_parser"] else [],
    }

    caminho_resultado = OCR_RESULTS_DIR / f"{timestamp}_{resultado_ocr['imagem_hash']}_{nome_base}.json"
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
