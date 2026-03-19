import shutil
from pathlib import Path

from app_paths import DATASET_DIR, LATEST_RESULT_PATH, ensure_runtime_dirs


def atualizar_ultimo_json(dataset_dir: Path = DATASET_DIR, destino: Path = LATEST_RESULT_PATH) -> Path:
    ensure_runtime_dirs()
    arquivos = sorted(dataset_dir.glob("*.json"), key=lambda item: item.stat().st_mtime)
    if not arquivos:
        raise FileNotFoundError("Nenhum arquivo JSON encontrado no dataset.")

    destino.parent.mkdir(parents=True, exist_ok=True)
    ultimo = arquivos[-1]
    shutil.copy2(ultimo, destino)
    return destino
