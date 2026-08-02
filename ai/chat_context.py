"""Kısa konuşma geçmişinden güvenli ürün bağlamı çıkarma yardımcıları."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any


@dataclass
class HistoryResolution:
    products: list[dict[str, Any]]
    ambiguous_product_names: list[str]


_CONTEXT_REFERENCE_MARKERS = (
    "bu bitki",
    "bu ürün",
    "bu takviye",
    "bunun",
    "onun",
    "bahsettiğin",
    "bahsettigin",
    "aynı bitki",
    "ayni bitki",
    "aynı ürün",
    "ayni urun",
)


def looks_like_context_follow_up(question: str) -> bool:
    normalized = str(question or "").strip().lower()
    return any(
        marker in normalized
        for marker in _CONTEXT_REFERENCE_MARKERS
    )


def history_user_messages(
    history: Sequence[Mapping[str, Any]] | None,
) -> list[str]:
    if not history:
        return []

    messages: list[str] = []

    for item in history[-8:]:
        if str(item.get("role") or "").strip().lower() != "user":
            continue

        content = str(item.get("content") or "").strip()
        if content:
            messages.append(content)

    return messages


def resolve_history_context(
    history: Sequence[Mapping[str, Any]] | None,
    resolve_products: Callable[[str], list[dict[str, Any]]],
) -> HistoryResolution:
    """En yakın önceki kullanıcı turundan ürün bağlamı çıkarır.

    Birden fazla ürün bulunan turda rastgele seçim yapılmaz.
    """

    for previous_question in reversed(
        history_user_messages(history)
    ):
        products = resolve_products(previous_question)

        if len(products) == 1:
            return HistoryResolution(
                products=products,
                ambiguous_product_names=[],
            )

        if len(products) > 1:
            return HistoryResolution(
                products=[],
                ambiguous_product_names=[
                    str(product.get("name") or "Belirtilmemiş").strip()
                    or "Belirtilmemiş"
                    for product in products
                ],
            )

    return HistoryResolution(
        products=[],
        ambiguous_product_names=[],
    )
