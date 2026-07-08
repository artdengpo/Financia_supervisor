# auth.py
# Вход, выход и проверка аутентификации

import streamlit as st
from database import get_or_create_user

def login_user(username):
    """
    Вход пользователя: сохраняет имя и ID в сессии.
    Возвращает True, если успешно.
    """
    if not username:
        return False
    user_id = get_or_create_user(username)
    st.session_state.user = username
    st.session_state.user_id = user_id
    return True

def logout_user():
    """Выход пользователя: очищает сессию и перезагружает страницу."""
    st.session_state.user = None
    st.session_state.user_id = None
    st.rerun()

def is_authenticated():
    """Проверяет, авторизован ли пользователь."""
    return st.session_state.get("user") is not None

def get_current_user():
    """Возвращает имя текущего пользователя или None."""
    return st.session_state.get("user")

def get_current_user_id():
    """Возвращает ID текущего пользователя или None."""
    return st.session_state.get("user_id")