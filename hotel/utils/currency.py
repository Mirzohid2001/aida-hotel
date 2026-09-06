from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _


class Currency(models.TextChoices):
    UZS = "UZS", _("UZS (so'm)")
    USD = "USD", _("USD ($)")
    EUR = "EUR", _("EUR (€)")


CURRENCY_LABELS = {
    Currency.UZS: "UZS",
    Currency.USD: "$",
    Currency.EUR: "€",
}


def currency_label(code: str | None) -> str:
    if not code:
        return CURRENCY_LABELS[Currency.UZS]
    return CURRENCY_LABELS.get(code, code)


def format_money(amount, code: str | None = None) -> str:
    """Human-readable amount + currency label (UZS without decimals, $/€ with 2)."""
    if amount is None:
        amount = Decimal("0")
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    code = code or Currency.UZS
    label = currency_label(code)
    if code == Currency.UZS:
        rendered = f"{amount.quantize(Decimal('1')):,.0f}".replace(",", " ")
    else:
        rendered = f"{amount.quantize(Decimal('0.01')):,.2f}"
    return f"{rendered} {label}"
