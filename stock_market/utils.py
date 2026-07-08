# utils.py
# Общие функции для форматирования и стилей

import pandas as pd
from datetime import datetime

def color_change(val):
    """Цвет для изменения цены (зелёный/красный)."""
    if val > 0:
        return 'color: green; font-weight: bold'
    elif val < 0:
        return 'color: red; font-weight: bold'
    return ''

def format_currency(value):
    """Форматирует число как валюту (доллары)."""
    if pd.isna(value):
        return "—"
    return f"${value:,.2f}"

def format_large_number(value):
    """Форматирует большие числа (объём, капитализация)."""
    if pd.isna(value):
        return "—"
    if value >= 1e9:
        return f"{value/1e9:.2f}B"
    elif value >= 1e6:
        return f"{value/1e6:.2f}M"
    else:
        return f"{value:,.0f}"

def get_last_update():
    """Возвращает текущее время в формате ДД.ММ.ГГГГ ЧЧ:ММ."""
    return datetime.now().strftime('%d.%m.%Y %H:%M')