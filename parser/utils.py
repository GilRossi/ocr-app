import os
import shutil

def atualizar_ultimo_json(dataset_dir="dataset", destino="public/ultimoreconhecimento.json"):
    arquivos = [
        os.path.join(dataset_dir, f)
        for f in os.listdir(dataset_dir)
        if f.endswith(".json")
    ]
    if not arquivos:
        print("❌ Nenhum arquivo JSON encontrado.")
        return

    ultimo = max(arquivos, key=os.path.getmtime)
    shutil.copy(ultimo, destino)
    print(f"✅ Último JSON copiado para: {destino}")
