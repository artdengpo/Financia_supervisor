# ml_engine.py
# ML-движок: рекомендации, технические сигналы, прогнозы

import pandas as pd
import numpy as np
import yfinance as yf
from config import SVD_N_FACTORS, SVD_N_EPOCHS, SVD_LR, SVD_REG
from surprise import SVD, Dataset, Reader
from sklearn.metrics.pairwise import cosine_similarity

# ------------------------------------------------------------
# Прогноз цены
# ------------------------------------------------------------
def predict_next_price(ticker):
    """Предсказывает цену на следующий день с помощью линейной регрессии."""
    try:
        hist = yf.Ticker(ticker).history(period='1mo')
        if len(hist) < 10:
            return None, None

        prices = hist['Close'].values
        days = np.arange(len(prices)).reshape(-1, 1)

        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(days, prices)

        next_day = np.array([[len(prices)]])
        next_price = model.predict(next_day)[0]
        last_price = prices[-1]
        change_percent = ((next_price - last_price) / last_price) * 100

        return next_price, change_percent
    except:
        return None, None

# ------------------------------------------------------------
# Технические индикаторы
# ------------------------------------------------------------
def calculate_momentum_score(stock_data):
    """Оценка момента (силы движения) акции."""
    try:
        hist = yf.Ticker(stock_data).history(period='1mo')
        if len(hist) < 20:
            return 'neutral'

        recent_5 = hist['Close'].pct_change().tail(5).mean()
        recent_20 = hist['Close'].pct_change().tail(20).mean()

        if recent_5 > 0.02 and recent_20 > 0.01:
            return 'strong_bullish'
        elif recent_5 > 0.005 and recent_20 > 0:
            return 'bullish'
        elif recent_5 < -0.02 and recent_20 < -0.01:
            return 'bearish'
        elif recent_5 < -0.005 and recent_20 < 0:
            return 'strong_bearish'
        else:
            return 'neutral'
    except:
        return 'neutral'

def get_technical_signal(ticker):
    """Сигнал по скользящим средним (SMA 20 и SMA 50)."""
    try:
        hist = yf.Ticker(ticker).history(period='3mo')
        if len(hist) < 50:
            return 'Нет данных'

        sma_20 = hist['Close'].rolling(20).mean().iloc[-1]
        sma_50 = hist['Close'].rolling(50).mean().iloc[-1]

        if sma_20 > sma_50:
            return '🟢 Бычий (рост)'
        elif sma_20 < sma_50:
            return '🔴 Медвежий (падение)'
        else:
            return '⚪ Нейтральный'
    except:
        return 'Ошибка'

# ------------------------------------------------------------
# Рекомендации
# ------------------------------------------------------------
def get_cold_start_recommendations(df, top_n=5):
    """Рекомендации для новых пользователей (без лайков)."""
    if df.empty:
        return df

    df_clean = df.copy()
    df_clean['Изменение %'] = df_clean['Изменение %'].fillna(0)
    df_clean['Объём'] = df_clean['Объём'].fillna(0)
    df_clean['Капитализация (B$)'] = df_clean['Капитализация (B$)'].fillna(0)

    max_change = df_clean['Изменение %'].max() or 1
    max_volume = df_clean['Объём'].max() or 1
    max_cap = df_clean['Капитализация (B$)'].max() or 1

    df_clean['Score'] = (
        (df_clean['Изменение %'] / max_change) * 0.5 +
        (df_clean['Объём'] / max_volume) * 0.3 +
        (df_clean['Капитализация (B$)'] / max_cap) * 0.2
    )

    return df_clean.sort_values(by='Score', ascending=False).head(top_n)

def get_item_based_recommendations(user_likes, all_likes_df, df, top_n=5):
    """Item-Based Collaborative Filtering."""
    if not user_likes or all_likes_df.empty:
        return None

    likes_filtered = all_likes_df[all_likes_df['liked'] == 1]
    if likes_filtered.empty:
        return None

    pivot = likes_filtered.pivot_table(index='user_id', columns='ticker', values='liked', fill_value=0)
    item_sim = cosine_similarity(pivot.T)
    item_sim_df = pd.DataFrame(item_sim, index=pivot.columns, columns=pivot.columns)

    similar_stocks = {}
    for ticker in user_likes:
        if ticker in item_sim_df.index:
            sim_series = item_sim_df[ticker].sort_values(ascending=False)
            for rec_ticker, score in sim_series.items():
                if rec_ticker != ticker and rec_ticker not in user_likes:
                    similar_stocks[rec_ticker] = similar_stocks.get(rec_ticker, 0) + score

    if not similar_stocks:
        return None

    sorted_recs = sorted(similar_stocks.items(), key=lambda x: x[1], reverse=True)
    top_tickers = [ticker for ticker, _ in sorted_recs[:top_n]]
    return df[df['Тикер'].isin(top_tickers)]

def get_svd_recommendations(user_id, df, all_likes, top_n=5):
    """Рекомендации на основе SVD (матричная факторизация)."""
    if all_likes.empty:
        return None

    if 'user_id' not in all_likes.columns or 'ticker' not in all_likes.columns or 'liked' not in all_likes.columns:
        return None

    all_tickers = df['Тикер'].unique()
    ticker_to_id = {ticker: i for i, ticker in enumerate(all_tickers)}

    data_for_surprise = all_likes.copy()
    data_for_surprise['ticker_id'] = data_for_surprise['ticker'].map(ticker_to_id)
    data_for_surprise = data_for_surprise.dropna(subset=['ticker_id'])

    if data_for_surprise.empty:
        return None

    reader = Reader(rating_scale=(0, 1))
    dataset = Dataset.load_from_df(data_for_surprise[['user_id', 'ticker_id', 'liked']], reader)
    trainset = dataset.build_full_trainset()

    algo = SVD(
        n_factors=SVD_N_FACTORS,
        n_epochs=SVD_N_EPOCHS,
        lr_all=SVD_LR,
        reg_all=SVD_REG
    )
    algo.fit(trainset)

    user_likes = set(all_likes[all_likes['user_id'] == user_id]['ticker'])
    candidates = set(all_tickers) - user_likes

    predictions = []
    for ticker in candidates:
        ticker_id = ticker_to_id.get(ticker)
        if ticker_id is not None:
            pred = algo.predict(user_id, ticker_id).est
            predictions.append((ticker, pred))

    predictions.sort(key=lambda x: x[1], reverse=True)
    top_tickers = [ticker for ticker, _ in predictions[:top_n]]

    return df[df['Тикер'].isin(top_tickers)]