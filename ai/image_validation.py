"""Görsel yükleme doğrulama sabitleri ve dosya imzası kontrolü."""

from __future__ import annotations

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


def detect_image_mime(image_bytes: bytes) -> str | None:
    """Dosya imzasından JPEG, PNG veya WEBP türünü doğrular."""

    if image_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"

    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"

    if (
        len(image_bytes) >= 12
        and image_bytes[:4] == b"RIFF"
        and image_bytes[8:12] == b"WEBP"
    ):
        return "image/webp"

    return None
