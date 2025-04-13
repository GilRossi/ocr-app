import os
import hashlib
import datetime
import json
import re
from google.cloud import vision
from .base_parser import extrair_promocoes

# Diretório onde os resultados ficarão salvos
DATASET_DIR = "dataset"
os.makedirs(DATASET_DIR, exist_ok=True)

# Função utilitária para gerar hash da imagem (para diferenciar cada input)
def gerar_hash(conteudo_bytes):
    return hashlib.sha256(conteudo_bytes).hexdigest()[:12]

# Função principal que roda múltiplas vezes e aplica o parser
def processar_imagem_vision(client: vision.ImageAnnotatorClient, imagem_bytes: bytes, execucoes: int = 100):
    hash_imagem = gerar_hash(imagem_bytes)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    resultados_ocr = []
    resultados_parser = []

    for i in range(execucoes):
        response = client.text_detection(image=vision.Image(content=imagem_bytes))
        textos = response.text_annotations

        if not textos:
            continue

        texto_ocr = textos[0].description
        resultados_ocr.append(texto_ocr)
        try:
            promocoes = extrair_promocoes(texto_ocr)
            resultados_parser.append(promocoes)
        except Exception as e:
            resultados_parser.append({"erro": str(e)})

    # Salvamento do resultado para futura análise/adaptação
    resultado_final = {
        "imagem_hash": hash_imagem,
        "timestamp": timestamp,
        "quantidade_execucoes": execucoes,
        "entradas_ocr": resultados_ocr,
        "resultados_parser": resultados_parser
    }

    nome_arquivo = f"{timestamp}_{hash_imagem}.json"
    caminho_arquivo = os.path.join(DATASET_DIR, nome_arquivo)

    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        json.dump(resultado_final, f, indent=2, ensure_ascii=False)

    return resultado_final
