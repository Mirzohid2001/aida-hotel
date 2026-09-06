from django import template

from hotel.utils.currency import currency_label, format_money

register = template.Library()


@register.filter
def money(amount, currency_code=None):
    """Format amount with currency. Usage: {{ price|money:site_settings.currency }}"""
    return format_money(amount, currency_code)


@register.filter
def money_label(currency_code):
    return currency_label(currency_code)
