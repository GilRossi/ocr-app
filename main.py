import os
import json
import logging
import subprocess
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from google.cloud import vision

# === Importa parser e utilitários ===
from parser.adaptive_parser import processar_imagem_vision
from parser.utils import atualizar_ultimo_json

# === Configuração de logs ===
logging.basicConfig(level=logging.INFO)

# === Inicializa o app FastAPI ===
app = FastAPI()

# === Instancia o cliente da Google Vision ===
client = vision.ImageAnnotatorClient()

# === Diretório de feedbacks ===
FEEDBACK_DIR = "feedbacks"
os.makedirs(FEEDBACK_DIR, exist_ok=True)

# === Mapeia o painel HTML ===
app.mount("/painel", StaticFiles(directory="public/painel", html=True), name="painel")

# === Redireciona "/" para o painel ===
@app.get("/", include_in_schema=False)
async def redirecionar_root():
    return RedirectResponse("/painel")


# === ENDPOINT OCR ====================================================
@app.post("/ocr")
async def ocr_vision(file: UploadFile = File(...), execucoes: int = 1):
    try:
        content = await file.read()
        logging.info(f"[OCR] Iniciando OCR com {execucoes} execuções... Arquivo: {file.filename}")

        resultado = processar_imagem_vision(client, content, execucoes)

        json_copiado = atualizar_ultimo_json()
        logging.info(f"[OCR] Resultado salvo e JSON copiado: {json_copiado}")

        return {
            "imagem_hash": resultado["imagem_hash"],
            "timestamp": resultado["timestamp"],
            "promocoes": resultado["resultados_parser"][0] if resultado["resultados_parser"] else [],
        }

    except Exception as e:
        logging.exception("Erro no endpoint /ocr")
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")


# === ENDPOINT FEEDBACK ===============================================
@app.post("/feedback")
async def receber_feedback(request: Request):
    try:
        dados = await request.json()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho = os.path.join(FEEDBACK_DIR, f"feedback_{timestamp}.json")

        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

        logging.info(f"[FEEDBACK] Feedback salvo: {caminho}")
        return {"status": "Feedback salvo com sucesso", "arquivo": caminho}

    except Exception as e:
        logging.exception("Erro no endpoint /feedback")
        raise HTTPException(status_code=400, detail=f"Erro ao receber feedback: {str(e)}")


# === ENDPOINT ATUALIZAR JSON PARA O PAINEL ============================
@app.post("/atualizar-json")
async def atualizar_json_endpoint():
    try:
        caminho = atualizar_ultimo_json()
        logging.info(f"[PAINEL] JSON atualizado para: {caminho}")
        return {"status": "Atualizado com sucesso", "arquivo": caminho}
    except Exception as e:
        logging.exception("Erro ao atualizar JSON")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar JSON: {str(e)}")


# === ENDPOINT APRENDIZADO ============================================
@app.post("/aprender")
async def rodar_aprendizado():
    try:
        logging.info("[APRENDIZADO] Executando script de aprendizado...")
        resultado = subprocess.run(
            ["python3", "parser/learn_parser.py"],
            capture_output=True,
            text=True
        )
        if resultado.returncode != 0:
            logging.error("[APRENDIZADO] Falha: " + resultado.stderr)
            raise RuntimeError(resultado.stderr)

        logging.info("[APRENDIZADO] Aprendizado concluído.")
        return {"status": "sucesso", "log": resultado.stdout}

    except Exception as e:
        logging.exception("Erro no aprendizado.")
        raise HTTPException(status_code=500, detail=f"Erro ao rodar aprendizado: {str(e)}")


# === ENDPOINT MÉTRICAS ===============================================
@app.get("/metricas")
async def obter_metricas():
    try:
        total, corretos = 0, 0

        for arquivo in os.listdir(FEEDBACK_DIR):
            if not arquivo.endswith(".json"):
                continue
            with open(os.path.join(FEEDBACK_DIR, arquivo), "r", encoding="utf-8") as f:
                dados = json.load(f)
                total += len(dados)
                corretos += sum(1 for item in dados if item.get("status") == "ok")

        precisao = round((corretos / total * 100), 2) if total else 0.0
        return {
            "total_feedbacks": total,
            "total_corretos": corretos,
            "precisao": precisao
        }

    except Exception as e:
        logging.exception("Erro ao calcular métricas.")
        raise HTTPException(status_code=500, detail=f"Erro ao calcular métricas: {str(e)}")


# === ENDPOINT GRÁFICO DE APRENDIZADO =================================
@app.get("/grafico")
async def obter_grafico():
    caminho = "grafico_aprendizado.png"
    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Gráfico não encontrado. Execute o aprendizado primeiro.")
    return FileResponse(caminho, media_type="image/png")
