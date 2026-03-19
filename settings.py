import os
from dataclasses import dataclass


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_env: str
    ocr_provider: str
    mock_ocr_text: str
    max_upload_bytes: int
    enable_docs: bool


def load_settings() -> Settings:
    provider = os.getenv("OCR_PROVIDER")
    if not provider:
        provider = "google" if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") else "mock"

    max_upload_mb = int(os.getenv("MAX_UPLOAD_MB", "10"))
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        ocr_provider=provider.lower(),
        mock_ocr_text=os.getenv(
            "MOCK_OCR_TEXT",
            "\n".join(
                [
                    "GELADINHO GOURMET DE MORANGO",
                    "R$ 8,99 R$ 6,99",
                    "A PARTIR DE 3 UN.",
                ]
            ),
        ),
        max_upload_bytes=max_upload_mb * 1024 * 1024,
        enable_docs=_get_bool("ENABLE_DOCS", True),
    )
