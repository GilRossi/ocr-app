import asyncio
import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException, UploadFile
from starlette.responses import FileResponse

import main
class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.feedback_dir = self.base_path / "feedbacks"
        self.feedback_dir.mkdir()
        self.latest_result_path = self.base_path / "ultimoreconhecimento.json"
        self.chart_path = self.base_path / "grafico_aprendizado.png"

        self.patches = [
            patch.object(main, "FEEDBACK_DIR", self.feedback_dir),
            patch.object(main, "LATEST_RESULT_PATH", self.latest_result_path),
            patch.object(main, "LEARNING_CHART_PATH", self.chart_path),
        ]
        for patcher in self.patches:
            patcher.start()

    def tearDown(self) -> None:
        for patcher in reversed(self.patches):
            patcher.stop()
        self.temp_dir.cleanup()

    def test_feedback_and_metrics_flow(self) -> None:
        payload = [
            main.FeedbackItem(
                produto="Sorvete Cremoso",
                preco_original="R$ 12,99",
                preco_promocional="R$ 9,99",
                condicao="A PARTIR DE 2 UN.",
                status="ok",
            ),
            main.FeedbackItem(
                produto="Chocolate",
                preco_original=None,
                preco_promocional="R$ 4,99",
                condicao=None,
                status="ajustar",
            ),
        ]

        response = asyncio.run(main.receber_feedback(payload))
        self.assertEqual(response["status"], "Feedback salvo com sucesso")

        metricas = asyncio.run(main.obter_metricas())
        self.assertEqual(metricas["total_feedbacks"], 2)
        self.assertEqual(metricas["total_corretos"], 1)
        self.assertEqual(metricas["precisao"], 50.0)

    def test_latest_json_endpoint_returns_saved_file(self) -> None:
        payload = {"promocoes": [{"produto": "Morango", "preco_promocional": "R$ 5,99"}]}
        self.latest_result_path.write_text(json.dumps(payload), encoding="utf-8")

        response = asyncio.run(main.obter_ultimo_json())
        self.assertIsInstance(response, FileResponse)
        self.assertEqual(Path(response.path), self.latest_result_path)

    def test_ocr_rejects_non_image_upload(self) -> None:
        upload = UploadFile(
            filename="teste.txt",
            file=BytesIO(b"conteudo"),
            headers={"content-type": "text/plain"},
        )
        with self.assertRaises(HTTPException) as context:
            main.validar_upload_imagem(upload, b"conteudo")
        self.assertEqual(context.exception.status_code, 400)

    def test_healthcheck_exposes_runtime_mode(self) -> None:
        response = asyncio.run(main.healthcheck())
        self.assertEqual(response["status"], "ok")
        self.assertIn(response["ocr_provider"], {"mock", "google"})

    def test_ocr_returns_promotions_in_mock_mode(self) -> None:
        class FakeUpload:
            filename = "encarte.png"
            content_type = "image/png"

            async def read(self) -> bytes:
                return b"fake-image"

        upload = FakeUpload()

        resultado_ocr = {
            "imagem_hash": "abc123def456",
            "timestamp": "20260319_131000",
            "ocr_provider": "mock",
            "resultados_parser": [
                [
                    {
                        "produto": "Geladinho Gourmet De Chocolate",
                        "preco_original": "R$ 10,99",
                        "preco_promocional": "R$ 7,99",
                        "condicao": "NA COMPRA DE 2 UN.",
                    }
                ]
            ],
        }

        with patch.object(main, "processar_ocr", return_value=resultado_ocr), patch.object(
            main,
            "atualizar_ultimo_json",
            return_value=self.latest_result_path,
        ):
            response = asyncio.run(main.ocr_vision(upload, 1))

        self.assertEqual(response["ocr_provider"], "mock")
        self.assertEqual(len(response["promocoes"]), 1)
        self.assertEqual(response["promocoes"][0]["produto"], "Geladinho Gourmet De Chocolate")


if __name__ == "__main__":
    unittest.main()
