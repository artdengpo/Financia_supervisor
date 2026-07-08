# streamlit run app.py
# app.py
# Главный файл приложения — интерфейс Streamlit

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import io

# Импорты из наших модулей
from config import TICKERS, CACHE_TTL, TOP_N_RECS
from database import get_user_likes, get_all_likes, get_username_by_id
from ml_engine import (
    get_cold_start_recommendations,
    get_item_based_recommendations,
    get_technical_signal,
    calculate_momentum_score,
    predict_next_price,
    get_svd_recommendations
)
from auth import login_user, logout_user, is_authenticated, get_current_user, get_current_user_id
from utils import color_change, format_currency, format_large_number, get_last_update

# ------------------------------------------------------------
# 1. ИНИЦИАЛИЗАЦИЯ СЕССИИ
# ------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ------------------------------------------------------------
# 2. НАСТРОЙКА СТРАНИЦЫ
# ------------------------------------------------------------
st.set_page_config(page_title="Финансовый смотритель", page_icon="📈", layout="wide")

# ------------------------------------------------------------
# 3. БОКОВАЯ ПАНЕЛЬ: ПРОФИЛЬ + НАВИГАЦИЯ
# ------------------------------------------------------------
st.sidebar.header("👤 Профиль")
if not is_authenticated():
    username = st.sidebar.text_input("Введите имя пользователя:")
    if st.sidebar.button("Войти"):
        if login_user(username):
            st.rerun()
        else:
            st.sidebar.warning("Введите имя")
else:
    st.sidebar.success(f"Привет, {get_current_user()}!")
    if st.sidebar.button("Выйти"):
        logout_user()

st.sidebar.divider()
page = st.sidebar.radio("Страница:", ["📋 Таблица", "❤️ Мои лайки", "🤖 Рекомендации", "🧠 AI Аналитика"])

# ------------------------------------------------------------
# 4. ЗАГРУЗКА ДАННЫХ
# ------------------------------------------------------------
st.title("📈 Финансовый смотритель")
st.caption(f"Данные на {get_last_update()}")

@st.cache_data(ttl=CACHE_TTL)
def load_data(tickers_dict):
    data = []
    for ticker, meta in tickers_dict.items():
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get('regularMarketPrice') or info.get('currentPrice')
            if price is None:
                hist = stock.history(period='1d')
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
            change = info.get('regularMarketChangePercent')
            if change is None:
                hist = stock.history(period='2d')
                if len(hist) >= 2:
                    prev = hist['Close'].iloc[-2]
                    curr = hist['Close'].iloc[-1]
                    change = ((curr - prev) / prev) * 100
            name = meta['name']
            sector = info.get('sector', 'N/A')
            country = meta['country']
            region = meta['region']
            market_cap = info.get('marketCap')
            volume = info.get('volume')
            data.append({
                'Тикер': ticker,
                'Название': name,
                'Страна': country,
                'Регион': region,
                'Сектор': sector,
                'Цена ($)': round(price, 2) if price else None,
                'Изменение %': round(change, 2) if change else None,
                'Объём': volume,
                'Капитализация (B$)': round(market_cap / 1e9, 2) if market_cap else None
            })
        except Exception as e:
            print(f"Ошибка загрузки {ticker}: {e}")
    df = pd.DataFrame(data)
    return df.dropna(subset=['Цена ($)', 'Изменение %'])

with st.spinner("🌍 Загружаем данные с мировых бирж..."):
    df = load_data(TICKERS)

if df.empty:
    st.error("❌ Не удалось загрузить данные. Проверьте интернет.")
    st.stop()

# ------------------------------------------------------------
# 5. БОКОВАЯ ПАНЕЛЬ: НАСТРОЙКИ
# ------------------------------------------------------------
st.sidebar.header("⚙️ Настройки")
sort_by = st.sidebar.selectbox(
    "Сортировка:",
    ["Без сортировки", "По росту 📈", "По падению 📉", "Сначала дорогие 💰", "Сначала дешёвые 💸", "По капитализации 🏛️"]
)
regions = ['Все'] + sorted(df['Регион'].unique().tolist())
selected_region = st.sidebar.selectbox("Фильтр по региону:", regions)
countries = ['Все'] + sorted(df['Страна'].unique().tolist())
selected_country = st.sidebar.selectbox("Фильтр по стране:", countries)
sectors = ['Все'] + sorted(df['Сектор'].unique().tolist())
selected_sector = st.sidebar.selectbox("Фильтр по сектору:", sectors)
search = st.sidebar.text_input("🔍 Поиск:", placeholder="AAPL или Apple")
if st.sidebar.button("🔄 Обновить данные"):
    st.cache_data.clear()
    st.rerun()

# ------------------------------------------------------------
# 6. ФИЛЬТРАЦИЯ И СОРТИРОВКА
# ------------------------------------------------------------
filtered_df = df.copy()
if selected_region != 'Все':
    filtered_df = filtered_df[filtered_df['Регион'] == selected_region]
if selected_country != 'Все':
    filtered_df = filtered_df[filtered_df['Страна'] == selected_country]
if selected_sector != 'Все':
    filtered_df = filtered_df[filtered_df['Сектор'] == selected_sector]
if search:
    s = search.upper()
    filtered_df = filtered_df[
        filtered_df['Тикер'].str.contains(s, na=False) |
        filtered_df['Название'].str.contains(s, na=False)
    ]

sort_map = {
    "По росту 📈": ('Изменение %', False),
    "По падению 📉": ('Изменение %', True),
    "Сначала дорогие 💰": ('Цена ($)', False),
    "Сначала дешёвые 💸": ('Цена ($)', True),
    "По капитализации 🏛️": ('Капитализация (B$)', False)
}
if sort_by in sort_map:
    col, asc = sort_map[sort_by]
    filtered_df = filtered_df.sort_values(by=col, ascending=asc)

# ------------------------------------------------------------
# 7. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ЛАЙКОВ
# ------------------------------------------------------------
def toggle_like(user, ticker):
    user_id = get_current_user_id()
    if user_id is None:
        return
    likes = get_user_likes(user_id)
    if ticker in likes:
        remove_like(user_id, ticker)
    else:
        add_like(user_id, ticker, liked=1)

def get_user_likes_list(user):
    if not user:
        return []
    user_id = get_current_user_id()
    if user_id is None:
        return []
    return get_user_likes(user_id)

# ------------------------------------------------------------
# 8. ОТОБРАЖЕНИЕ СТРАНИЦ
# ------------------------------------------------------------
if page == "📋 Таблица":
    st.write(f"**Найдено: {len(filtered_df)} акций**")

    user = get_current_user()
    user_likes = get_user_likes_list(user) if user else []

    # Рисуем таблицу вручную с кнопками
    for idx, row in filtered_df.iterrows():
        cols = st.columns([1, 2, 1.2, 1, 1.5, 1.5, 1, 1.2, 0.8])
        ticker = row['Тикер']

        cols[0].write(f"**{ticker}**")
        cols[1].write(row['Название'])
        cols[2].write(format_currency(row['Цена ($)']))
        change = row['Изменение %']
        if change > 0:
            cols[3].markdown(f"<span style='color:green; font-weight:bold'>{change:.2f}%</span>", unsafe_allow_html=True)
        elif change < 0:
            cols[3].markdown(f"<span style='color:red; font-weight:bold'>{change:.2f}%</span>", unsafe_allow_html=True)
        else:
            cols[3].write(f"{change:.2f}%")
        cols[4].write(format_large_number(row['Объём']))
        cols[5].write(format_large_number(row['Капитализация (B$)']))
        cols[6].write(row['Сектор'])
        signal = get_technical_signal(ticker)
        cols[7].write(signal)

        if user:
            is_liked = ticker in user_likes
            label = "❤️" if is_liked else "🤍"
            if cols[8].button(label, key=f"like_{ticker}"):
                toggle_like(user, ticker)
                st.rerun()
        else:
            cols[8].write("🔒")

    # Графики и статистика
    st.divider()
    st.subheader("📊 Изменение цен за день")
    chart_data = filtered_df[['Тикер', 'Изменение %']].copy()
    chart_data = chart_data.set_index('Тикер')
    st.bar_chart(chart_data, height=300, use_container_width=True)

    st.divider()
    st.subheader("📈 График цены за период")
    selected_ticker = st.selectbox("Выберите акцию:", options=filtered_df['Тикер'].tolist(), index=0)
    period = st.select_slider("Период:", options=["1mo", "3mo", "6mo", "1y", "2y"], value="3mo")
    if selected_ticker:
        try:
            hist = yf.Ticker(selected_ticker).history(period=period)
            if not hist.empty:
                hist_close = hist[['Close']].rename(columns={'Close': 'Цена ($)'})
                st.line_chart(hist_close, height=300, use_container_width=True)
            else:
                st.warning("Нет данных за выбранный период.")
        except Exception as e:
            st.error(f"Ошибка загрузки графика: {e}")

    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Всего акций", len(filtered_df))
    with col2:
        avg = filtered_df['Изменение %'].mean()
        st.metric("📈 Среднее изменение", f"{avg:.2f}%")
    with col3:
        st.metric("🚀 Макс. рост", f"{filtered_df['Изменение %'].max():.2f}%")
    with col4:
        st.metric("📉 Макс. падение", f"{filtered_df['Изменение %'].min():.2f}%")

    # Экспорт в Excel
    st.divider()
    st.subheader("📥 Экспорт данных")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Акции')
        writer.close()
    st.download_button(
        label="📊 Скачать данные в Excel",
        data=buffer.getvalue(),
        file_name=f"stocks_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ------------------------------------------------------------
# СТРАНИЦА «МОИ ЛАЙКИ»
# ------------------------------------------------------------
elif page == "❤️ Мои лайки":
    st.subheader("❤️ Ваши лайкнутые акции")
    user = get_current_user()
    if not user:
        st.warning("Войдите в профиль, чтобы видеть свои лайки.")
    else:
        likes = get_user_likes_list(user)
        if not likes:
            st.info("Вы ещё не лайкнули ни одной акции.")
        else:
            liked_df = df[df['Тикер'].isin(likes)]
            if not liked_df.empty:
                st.dataframe(liked_df, use_container_width=True)
            else:
                st.info("Нет данных по лайкнутым акциям.")

# ------------------------------------------------------------
# СТРАНИЦА «РЕКОМЕНДАЦИИ»
# ------------------------------------------------------------
elif page == "🤖 Рекомендации":
    st.subheader("🤖 Персональные рекомендации")
    user = get_current_user()
    if not user:
        st.warning("Войдите в профиль, чтобы получать рекомендации.")
    else:
        user_id = get_current_user_id()
        all_likes = get_all_likes()

        if all_likes.empty:
            st.info("Пока нет данных о лайках. Ставьте лайки, чтобы система могла дать рекомендации.")
        else:
            model_choice = st.radio(
                "Выберите модель рекомендаций:",
                ["Косинусная близость (пользователи)", "SVD (матричная факторизация)"],
                index=1
            )

            if model_choice == "Косинусная близость (пользователи)":
                pivot = all_likes.pivot_table(index='user_id', columns='ticker', values='liked', fill_value=0)
                if user_id not in pivot.index:
                    st.info("Вы ещё не лайкнули ни одной акции.")
                    st.stop()

                sim_matrix = cosine_similarity(pivot.values)
                np.fill_diagonal(sim_matrix, 0)
                user_idx = pivot.index.get_loc(user_id)
                sim_scores = sim_matrix[user_idx]

                similar_users = np.argsort(sim_scores)[-3:][::-1]
                similar_users_ids = pivot.index[similar_users].tolist()

                my_likes = set(get_user_likes(user_id))
                recommendations = []
                for sim_user in similar_users_ids:
                    user_likes_set = set(pivot.loc[sim_user][pivot.loc[sim_user] == 1].index)
                    new_likes = user_likes_set - my_likes
                    recommendations.extend(new_likes)

                unique_recs = list(dict.fromkeys(recommendations))
                if not unique_recs:
                    st.info("Похожие пользователи не нашли новых акций для вас.")
                else:
                    rec_df = df[df['Тикер'].isin(unique_recs)]
                    st.write(f"**Найдено {len(rec_df)} акций (косинусная близость):**")
                    st.dataframe(rec_df, use_container_width=True)
                    with st.expander("Кто из похожих пользователей это лайкнул?"):
                        for ticker in unique_recs[:10]:
                            users_list = []
                            for sim_user in similar_users_ids:
                                if pivot.loc[sim_user, ticker] == 1:
                                    name = get_username_by_id(sim_user)
                                    if name:
                                        users_list.append(name)
                            if users_list:
                                st.write(f"**{ticker}**: {', '.join(users_list)}")
            else:
                st.info("🧠 Используем SVD (матричную факторизацию).")
                rec_df = get_svd_recommendations(user_id, df, all_likes, top_n=TOP_N_RECS)
                if rec_df is not None and not rec_df.empty:
                    st.write(f"**SVD рекомендует {len(rec_df)} акций:**")
                    st.dataframe(rec_df, use_container_width=True)
                else:
                    st.info("SVD не нашёл рекомендаций. Попробуйте поставить больше лайков.")

# ------------------------------------------------------------
# СТРАНИЦА «AI АНАЛИТИКА»
# ------------------------------------------------------------
elif page == "🧠 AI Аналитика":
    st.subheader("🧠 AI-советник по акциям")
    user = get_current_user()
    user_likes = get_user_likes_list(user) if user else []

    if not user_likes:
        st.info("👋 Вы новый пользователь! AI подбирает для вас самые перспективные акции.")
        cold_recs = get_cold_start_recommendations(filtered_df, top_n=TOP_N_RECS)
        if cold_recs is not None and not cold_recs.empty:
            st.write("🏆 **Топ-5 акций для старта:**")
            st.dataframe(cold_recs[['Тикер', 'Название', 'Цена ($)', 'Изменение %', 'Объём', 'Капитализация (B$)']],
                         use_container_width=True)
        else:
            st.warning("Недостаточно данных для анализа.")
    else:
        st.info("🎯 AI анализирует ваши лайки и ищет похожие акции.")
        all_likes = get_all_likes()
        item_recs = get_item_based_recommendations(user_likes, all_likes, filtered_df, top_n=TOP_N_RECS)
        if item_recs is not None and not item_recs.empty:
            st.write("🔗 **Акции, которые часто лайкают вместе с вашими:**")
            st.dataframe(item_recs[['Тикер', 'Название', 'Цена ($)', 'Изменение %', 'Сектор']],
                         use_container_width=True)
        else:
            st.info("Пока недостаточно данных. Поставьте больше лайков!")

        # Детальный анализ конкретной акции
        st.divider()
        st.subheader("📊 Детальный AI-анализ акции")
        selected_ticker = st.selectbox("Выберите акцию для анализа:", options=filtered_df['Тикер'].tolist(), key="ai_analysis_ticker")
        if selected_ticker:
            signal = get_technical_signal(selected_ticker)
            momentum = calculate_momentum_score(selected_ticker)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("📈 Тренд (SMA)", signal)
            with col2:
                emoji = "🚀" if momentum == "strong_bullish" else "📈" if momentum == "bullish" else "➖" if momentum == "neutral" else "📉"
                st.metric("💪 Момент (динамика)", f"{emoji} {momentum.replace('_', ' ').title()}")

            # График со скользящими средними
            try:
                hist = yf.Ticker(selected_ticker).history(period='3mo')
                if not hist.empty:
                    hist['SMA_20'] = hist['Close'].rolling(20).mean()
                    hist['SMA_50'] = hist['Close'].rolling(50).mean()
                    st.write("📉 **График цены со SMA 20 и SMA 50:**")
                    st.line_chart(hist[['Close', 'SMA_20', 'SMA_50']], height=300, use_container_width=True)
                    last_sma20 = hist['SMA_20'].iloc[-1]
                    last_sma50 = hist['SMA_50'].iloc[-1]
                    if last_sma20 > last_sma50:
                        st.success("✅ Бычий сигнал: SMA 20 выше SMA 50. Рекомендуется покупка.")
                    else:
                        st.warning("⚠️ Медвежий сигнал: SMA 20 ниже SMA 50. Воздержаться от покупки.")
            except Exception as e:
                st.error(f"Ошибка загрузки графика: {e}")

            # Прогноз цены
            st.divider()
            st.subheader("🔮 Прогноз цены на завтра (линейная регрессия)")
            if st.button("Рассчитать прогноз", key="predict_btn"):
                next_price, change = predict_next_price(selected_ticker)
                if next_price:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📊 Прогноз цены", f"${next_price:.2f}")
                    with col2:
                        emoji = "🟢" if change > 0 else "🔴"
                        st.metric("📈 Изменение", f"{emoji} {change:.2f}%")
                else:
                    st.warning("Недостаточно данных для прогноза.")