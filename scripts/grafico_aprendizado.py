import json
import os
import tempfile

os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "ocr-app-matplotlib"))
import matplotlib

from app_paths import FEEDBACK_DIR, LEARNING_CHART_PATH, ensure_runtime_dirs


matplotlib.use("Agg")
import matplotlib.pyplot as plt


ensure_runtime_dirs()


def gerar_grafico_aprendizado():
    arquivos = sorted(FEEDBACK_DIR.glob("*.json"))
    precisoes: list[float] = []
    nomes: list[str] = []

    for arquivo in arquivos:
        dados = json.loads(arquivo.read_text(encoding="utf-8"))
        total = len(dados)
        corretos = sum(1 for item in dados if item.get("status") == "ok")
        precisao = round((corretos / total) * 100, 2) if total > 0 else 0.0
        precisoes.append(precisao)
        nomes.append(arquivo.stem.replace("feedback_", ""))

    plt.figure(figsize=(10, 5))
    if precisoes:
        plt.plot(nomes, precisoes, marker="o", linestyle="-", color="blue")
    else:
        plt.plot([], [])
    plt.title("Evolução da Precisão dos Feedbacks")
    plt.xlabel("Execução")
    plt.ylabel("Precisão (%)")
    plt.xticks(rotation=45, ha="right")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(LEARNING_CHART_PATH)
    plt.close()
    return LEARNING_CHART_PATH


if __name__ == "__main__":
    print(gerar_grafico_aprendizado())
