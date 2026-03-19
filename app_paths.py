from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"
FEEDBACK_DIR = BASE_DIR / "feedbacks"
PUBLIC_DIR = BASE_DIR / "public"
PAINEL_DIR = PUBLIC_DIR / "painel"
LATEST_RESULT_PATH = PUBLIC_DIR / "ultimoreconhecimento.json"
RESULTADO_JSON_PATH = PUBLIC_DIR / "resultado.json"
LEARNING_RULES_PATH = DATASET_DIR / "parser_learning_rules.json"
LEARNING_CHART_PATH = BASE_DIR / "grafico_aprendizado.png"
OCR_TEXT_DIR = DATASET_DIR / "ocr"
OCR_RESULTS_DIR = DATASET_DIR / "resultados"


def ensure_runtime_dirs() -> None:
    DATASET_DIR.mkdir(exist_ok=True)
    FEEDBACK_DIR.mkdir(exist_ok=True)
    PUBLIC_DIR.mkdir(exist_ok=True)
    PAINEL_DIR.mkdir(exist_ok=True)
    OCR_TEXT_DIR.mkdir(exist_ok=True)
    OCR_RESULTS_DIR.mkdir(exist_ok=True)
