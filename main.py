import json
import logging
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from google.cloud import vision
from pydantic import BaseModel, Field

from app_paths import FEEDBACK_DIR, LATEST_RESULT_PATH, LEARNING_CHART_PATH, PAINEL_DIR, ensure_runtime_dirs
from parser.adaptive_parser import processar_imagem_vision
from parser.learn_parser import aplicar_aprendizado_incremental
from parser.utils import atualizar_ultimo_json
from scripts.grafico_aprendizado import gerar_grafico_aprendizado


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ensure_runtime_dirs()

app = FastAPI(title="OCR App", version="1.0.0")
app.mount("/painel", StaticFiles(directory=str(PAINEL_DIR), html=True), name="painel")

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


class FeedbackItem(BaseModel):
    produto: str = Field(min_length=1, max_length=200)
    preco_original: str | None = Field(default=None, max_length=50)
    preco_promocional: str = Field(min_length=1, max_length=50)
    condicao: str | None = Field(default=None, max_length=200)
    status: Literal["ok", "ajustar"]


@lru_cache(maxsize=1)
def get_vision_client() -> vision.ImageAnnotatorClient:
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise RuntimeError("A variável GOOGLE_APPLICATION_CREDENTIALS não foi definida.")
    if not Path(credentials_path).exists():
        raise RuntimeError("O arquivo de credenciais configurado não existe.")
    return vision.ImageAnnotatorClient()


def validar_upload_imagem(file: UploadFile, content: bytes) -> None:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Envie um arquivo de imagem válido.")
    if not content:
        raise HTTPException(status_code=400, detail="O arquivo enviado está vazio.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="A imagem excede o limite de 10 MB.")


@app.get("/", include_in_schema=False)
async def redirecionar_root() -> RedirectResponse:
    return RedirectResponse("/painel")


@app.get("/ultimoreconhecimento.json", include_in_schema=False)
async def obter_ultimo_json() -> FileResponse:
    if not LATEST_RESULT_PATH.exists():
        raise HTTPException(status_code=404, detail="Nenhum reconhecimento disponível.")
    return FileResponse(LATEST_RESULT_PATH, media_type="application/json")


@app.post("/ocr")
async def ocr_vision(
    file: UploadFile = File(...),
    execucoes: int = Query(default=1, ge=1, le=5),
) -> dict:
    try:
        content = await file.read()
        validar_upload_imagem(file, content)
        logger.info("[OCR] Iniciando OCR com %s execuções. Arquivo: %s", execucoes, file.filename)

        resultado = processar_imagem_vision(get_vision_client(), content, execucoes)
        caminho_atualizado = atualizar_ultimo_json()
        logger.info("[OCR] Resultado atualizado em %s", caminho_atualizado)

        return {
            "imagem_hash": resultado["imagem_hash"],
            "timestamp": resultado["timestamp"],
            "promocoes": resultado["resultados_parser"][0] if resultado["resultados_parser"] else [],
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Erro no endpoint /ocr")
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {exc}") from exc


@app.post("/feedback")
async def receber_feedback(feedbacks: list[FeedbackItem]) -> dict:
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = FEEDBACK_DIR / f"feedback_{timestamp}.json"
        while nome_arquivo.exists():
            timestamp = f"{timestamp}_1"
            nome_arquivo = FEEDBACK_DIR / f"feedback_{timestamp}.json"

        conteudo = [item.model_dump() for item in feedbacks]
        nome_arquivo.write_text(
            json.dumps(conteudo, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        logger.info("[FEEDBACK] Feedback salvo em %s", nome_arquivo)
        return {"status": "Feedback salvo com sucesso", "arquivo": str(nome_arquivo)}
    except Exception as exc:
        logger.exception("Erro no endpoint /feedback")
        raise HTTPException(status_code=400, detail=f"Erro ao receber feedback: {exc}") from exc


@app.post("/atualizar-json")
async def atualizar_json_endpoint() -> dict:
    try:
        caminho = atualizar_ultimo_json()
        logger.info("[PAINEL] JSON atualizado para %s", caminho)
        return {"status": "Atualizado com sucesso", "arquivo": str(caminho)}
    except Exception as exc:
        logger.exception("Erro ao atualizar JSON")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar JSON: {exc}") from exc


@app.post("/aprender")
async def rodar_aprendizado() -> dict:
    try:
        logger.info("[APRENDIZADO] Executando aprendizado incremental...")
        resumo = aplicar_aprendizado_incremental()
        grafico = gerar_grafico_aprendizado()
        return {"status": "sucesso", "resumo": resumo, "grafico": str(grafico)}
    except Exception as exc:
        logger.exception("Erro no aprendizado")
        raise HTTPException(status_code=500, detail=f"Erro ao rodar aprendizado: {exc}") from exc


@app.get("/metricas")
async def obter_metricas() -> dict:
    try:
        total, corretos = 0, 0
        for arquivo in FEEDBACK_DIR.glob("*.json"):
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
            total += len(dados)
            corretos += sum(1 for item in dados if item.get("status") == "ok")

        precisao = round((corretos / total * 100), 2) if total else 0.0
        return {
            "total_feedbacks": total,
            "total_corretos": corretos,
            "precisao": precisao,
        }
    except Exception as exc:
        logger.exception("Erro ao calcular métricas")
        raise HTTPException(status_code=500, detail=f"Erro ao calcular métricas: {exc}") from exc


@app.get("/grafico")
async def obter_grafico() -> FileResponse:
    if not LEARNING_CHART_PATH.exists():
        raise HTTPException(status_code=404, detail="Gráfico não encontrado. Execute o aprendizado primeiro.")
    return FileResponse(LEARNING_CHART_PATH, media_type="image/png")
