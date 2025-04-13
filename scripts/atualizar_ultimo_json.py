import os
import shutil
from glob import glob

# Caminhos
PASTA_ORIGEM = "dataset"  # ou "resultados", ajuste conforme seu projeto
ARQUIVO_DESTINO = "public/ultimoreconhecimento.json"

def encontrar_mais_recente():
    arquivos = glob(os.path.join(PASTA_ORIGEM, "*.json"))
    if not arquivos:
        raise FileNotFoundError("Nenhum arquivo JSON encontrado na pasta de origem.")

    mais_recente = max(arquivos, key=os.path.getmtime)
    return mais_recente

def copiar_para_publico():
    origem = encontrar_mais_recente()
    shutil.copy2(origem, ARQUIVO_DESTINO)
    print(f"✅ Último JSON copiado: {origem} → {ARQUIVO_DESTINO}")

if __name__ == "__main__":
    try:
        copiar_para_publico()
    except Exception as e:
        print(f"❌ Erro: {e}")
