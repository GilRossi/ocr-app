import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from parser import base_parser


class ParserTests(unittest.TestCase):
    def test_extract_promotions_with_condition(self) -> None:
        texto = "\n".join(
            [
                "GELADINHO GOURMET DE MORANGO",
                "R$ 8,99 R$ 6,99",
                "A PARTIR DE 3 UN.",
            ]
        )

        promocoes = base_parser.extrair_promocoes(texto)

        self.assertEqual(len(promocoes), 1)
        self.assertEqual(promocoes[0]["produto"], "Geladinho Gourmet De Morango")
        self.assertEqual(promocoes[0]["preco_original"], "R$ 8,99")
        self.assertEqual(promocoes[0]["preco_promocional"], "R$ 6,99")
        self.assertEqual(promocoes[0]["condicao"], "A PARTIR DE 3 UN.")

    def test_learning_persists_condition_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_path = Path(temp_dir) / "learning_rules.json"
            exemplos = [
                {
                    "produto": "Produto Teste",
                    "preco_promocional": "R$ 5,99",
                    "condicao": "NA COMPRA DE 2 UNIDADES",
                    "status": "ajustar",
                }
            ]

            with patch.object(base_parser, "LEARNING_RULES_PATH", rules_path):
                resumo = base_parser.ajustar_regex_dinamicamente(exemplos)
                rules = json.loads(rules_path.read_text(encoding="utf-8"))

            self.assertEqual(resumo["examples_processed"], 1)
            self.assertIn("NA COMPRA DE 2 UNIDADES", rules["condition_markers"])


if __name__ == "__main__":
    unittest.main()
