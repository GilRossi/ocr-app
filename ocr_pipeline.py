import os
import json
import hashlib
from datetime import datetime
from google.cloud import vision
from parser.base_parser import extrair_promocoes

# Configurações
IMAGENS_DIR = "dataset/imagens"
OCR_DIR = "dataset/ocr"
RESULTADOS_DIR = "dataset/resultados"

# Cria diretórios se não existirem
os.makedirs(OCR_DIR, exist_ok=True)
os.makedirs(RESULTADOS_DIR, exist_ok=True)

# Cliente do Google Vision
client = vision.ImageAnnotatorClient()

def gerar_hash(conteudo):
    return hashlib.sha256(conteudo).hexdigest()[:12]

def processar_imagem(caminho_imagem):
    with open(caminho_imagem, "rb") as f:
        imagem_bytes = f.read()

    hash_img = gerar_hash(imagem_bytes)
    nome_base = os.path.splitext(os.path.basename(caminho_imagem))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # OCR
    response = client.text_detection(image=vision.Image(content=imagem_bytes))
    textos = response.text_annotations
    texto_ocr = textos[0].description if textos else ""

    # Salva OCR bruto
    with open(f"{OCR_DIR}/{timestamp}_{hash_img}_{nome_base}.txt", "w", encoding="utf-8") as f:
        f.write(texto_ocr)

    # Parser
    try:
        promocoes = extrair_promocoes(texto_ocr)
    except Exception as e:
        promocoes = [{"erro": str(e)}]

    # Salva resultado final
    resultado = {
        "arquivo": nome_base,
        "imagem_hash": hash_img,
        "timestamp": timestamp,
        "texto_ocr": texto_ocr,
        "promocoes": promocoes
    }

    with open(f"{RESULTADOS_DIR}/{timestamp}_{hash_img}_{nome_base}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    print(f"✅ Processado: {nome_base} | {len(promocoes)} promoções encontradas.")

def rodar_pipeline():
    imagens = [
        f for f in os.listdir(IMAGENS_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if not imagens:
        print("⚠️ Nenhuma imagem encontrada em 'dataset/imagens'.")
        return

    for imagem in imagens:
        caminho = os.path.join(IMAGENS_DIR, imagem)
        processar_imagem(caminho)

if __name__ == "__main__":
    rodar_pipeline()