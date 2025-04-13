import os
import json
import matplotlib.pyplot as plt

# Caminho da pasta com os feedbacks
FEEDBACK_DIR = "feedbacks"
ARQUIVOS = sorted([f for f in os.listdir(FEEDBACK_DIR) if f.endswith(".json")])

precisoes = []
nomes = []

for arquivo in ARQUIVOS:
    caminho = os.path.join(FEEDBACK_DIR, arquivo)
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    total = len(dados)
    corretos = sum(1 for item in dados if item.get("status") == "ok")
    precisao = round((corretos / total) * 100, 2) if total > 0 else 0.0

    precisoes.append(precisao)
    nomes.append(arquivo.replace("feedback_", "").replace(".json", ""))

    print(f"[{arquivo}] Total: {total}, OK: {corretos}, Precisão: {precisao}%")

# Gera o gráfico
plt.figure(figsize=(10, 5))
plt.plot(nomes, precisoes, marker='o', linestyle='-', color='blue')
plt.title("Evolução da Precisão dos Feedbacks")
plt.xlabel("Execução")
plt.ylabel("Precisão (%)")
plt.xticks(rotation=45, ha="right")
plt.grid(True)
plt.tight_layout()
plt.savefig("grafico_aprendizado.png")
plt.show()

print("\n✅ Gráfico salvo como 'grafico_aprendizado.png'")