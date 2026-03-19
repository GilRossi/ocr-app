import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services import ocr_service
from settings import Settings


class OcrServiceTests(unittest.TestCase):
    def test_processar_ocr_em_modo_mock_persiste_resultado(self) -> None:
        settings = Settings(
            app_env="test",
            ocr_provider="mock",
            mock_ocr_text="PICOLÉ DE UVA\nR$ 5,99 R$ 4,49\nA PARTIR DE 2 UN.",
            max_upload_bytes=1024,
            enable_docs=True,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            dataset_dir = Path(temp_dir)
            with patch.object(ocr_service, "DATASET_DIR", dataset_dir):
                resultado = ocr_service.processar_ocr(b"imagem-falsa", 1, settings)

            self.assertEqual(resultado["ocr_provider"], "mock")
            self.assertEqual(len(resultado["resultados_parser"][0]), 1)
            self.assertTrue(Path(resultado["arquivo_resultado"]).exists())


if __name__ == "__main__":
    unittest.main()
