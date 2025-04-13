import sys
import os
sys.path.append(os.path.abspath("."))

import json
from parser.base_parser import extrair_promocoes
from difflib import SequenceMatcher

DATASET_DIR = "dataset"

def similaridade(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def aprender_com_dataset(threshold=0.7):
    arquivos = [f for f in os.listdir(DATASET_DIR) if f.endswith(".json")]
    total = 0
    ajustaveis = 0

    for nome_arquivo in arquivos:
        caminho = os.path.join(DATASET_DIR, nome_arquivo)
        with open(caminho, encoding='utf-8') as f:
            dados = json.load(f)

        entradas_ocr = dados.get("entradas_ocr", [])
        resultados_parser = dados.get("resultados_parser", [])

        if not entradas_ocr or not resultados_parser:
            continue

        texto = entradas_ocr[0]  # pega o OCR da primeira execução
        resultado_antigo = resultados_parser[0] if isinstance(resultados_parser[0], list) else []

        # Roda o parser atual
        novo_resultado = extrair_promocoes(texto)

        # Compara resultados
        for novo in novo_resultado:
            if not any(
                similaridade(novo['produto'], antigo.get('produto', '')) >= threshold
                for antigo in resultado_antigo
            ):
                print(f"❌ Não reconhecido corretamente: {novo['produto']}")
                ajustaveis += 1

        total += len(novo_resultado)

    print("\n📊 RESUMO DO APRENDIZADO")
    print(f"Total de produtos analisados: {total}")
    print(f"Produtos com baixa similaridade: {ajustaveis}")
    print(f"Precisão atual: {100 * (total - ajustaveis) / total:.2f}%")

if __name__ == "__main__":
    aprender_com_dataset()
