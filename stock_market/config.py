
TICKERS = {
    'AAPL': {'name': 'Apple Inc.', 'country': 'США', 'region': 'Северная Америка'},
    'MSFT': {'name': 'Microsoft', 'country': 'США', 'region': 'Северная Америка'},
    'GOOGL': {'name': 'Alphabet (Google)', 'country': 'США', 'region': 'Северная Америка'},
    'AMZN': {'name': 'Amazon', 'country': 'США', 'region': 'Северная Америка'},
    'META': {'name': 'Meta (Facebook)', 'country': 'США', 'region': 'Северная Америка'},
    'TSLA': {'name': 'Tesla', 'country': 'США', 'region': 'Северная Америка'},
    'NVDA': {'name': 'NVIDIA', 'country': 'США', 'region': 'Северная Америка'},
    'JPM': {'name': 'JPMorgan Chase', 'country': 'США', 'region': 'Северная Америка'},
    'V': {'name': 'Visa', 'country': 'США', 'region': 'Северная Америка'},
    'JNJ': {'name': 'Johnson & Johnson', 'country': 'США', 'region': 'Северная Америка'},
    'WMT': {'name': 'Walmart', 'country': 'США', 'region': 'Северная Америка'},
    'PG': {'name': 'Procter & Gamble', 'country': 'США', 'region': 'Северная Америка'},
    'UNH': {'name': 'UnitedHealth', 'country': 'США', 'region': 'Северная Америка'},
    'HD': {'name': 'Home Depot', 'country': 'США', 'region': 'Северная Америка'},
    'DIS': {'name': 'Disney', 'country': 'США', 'region': 'Северная Америка'},
    'MA': {'name': 'Mastercard', 'country': 'США', 'region': 'Северная Америка'},
    'BAC': {'name': 'Bank of America', 'country': 'США', 'region': 'Северная Америка'},
    'NFLX': {'name': 'Netflix', 'country': 'США', 'region': 'Северная Америка'},
    'ADBE': {'name': 'Adobe', 'country': 'США', 'region': 'Северная Америка'},
    'CRM': {'name': 'Salesforce', 'country': 'США', 'region': 'Северная Америка'},
    'AMD': {'name': 'AMD', 'country': 'США', 'region': 'Северная Америка'},
    'INTC': {'name': 'Intel', 'country': 'США', 'region': 'Северная Америка'},
    'CSCO': {'name': 'Cisco', 'country': 'США', 'region': 'Северная Америка'},
    'PFE': {'name': 'Pfizer', 'country': 'США', 'region': 'Северная Америка'},
    'ABT': {'name': 'Abbott Laboratories', 'country': 'США', 'region': 'Северная Америка'},
    'TMO': {'name': 'Thermo Fisher', 'country': 'США', 'region': 'Северная Америка'},
    'COST': {'name': 'Costco', 'country': 'США', 'region': 'Северная Америка'},
    'NKE': {'name': 'Nike', 'country': 'США', 'region': 'Северная Америка'},
    'HON': {'name': 'Honeywell', 'country': 'США', 'region': 'Северная Америка'},
    'IBM': {'name': 'IBM', 'country': 'США', 'region': 'Северная Америка'},
    'GE': {'name': 'General Electric', 'country': 'США', 'region': 'Северная Америка'},
    'CAT': {'name': 'Caterpillar', 'country': 'США', 'region': 'Северная Америка'},
    'LOW': {'name': "Lowe's", 'country': 'США', 'region': 'Северная Америка'},
    'GS': {'name': 'Goldman Sachs', 'country': 'США', 'region': 'Северная Америка'},
    'AXP': {'name': 'American Express', 'country': 'США', 'region': 'Северная Америка'},
    'MS': {'name': 'Morgan Stanley', 'country': 'США', 'region': 'Северная Америка'},
    'C': {'name': 'Citigroup', 'country': 'США', 'region': 'Северная Америка'},
    'WFC': {'name': 'Wells Fargo', 'country': 'США', 'region': 'Северная Америка'},
    'PLD': {'name': 'Prologis', 'country': 'США', 'region': 'Северная Америка'},
    'DE': {'name': 'Deere & Co', 'country': 'США', 'region': 'Северная Америка'},

    # Россия
    'SBER.ME': {'name': 'Сбербанк', 'country': 'Россия', 'region': 'Россия'},
    'GAZP.ME': {'name': 'Газпром', 'country': 'Россия', 'region': 'Россия'},
    'LKOH.ME': {'name': 'Лукойл', 'country': 'Россия', 'region': 'Россия'},
    'ROSN.ME': {'name': 'Роснефть', 'country': 'Россия', 'region': 'Россия'},
    'GMKN.ME': {'name': 'Норникель', 'country': 'Россия', 'region': 'Россия'},
    'NVTK.ME': {'name': 'Новатэк', 'country': 'Россия', 'region': 'Россия'},
    'MTSS.ME': {'name': 'МТС', 'country': 'Россия', 'region': 'Россия'},
    'TATN.ME': {'name': 'Татнефть', 'country': 'Россия', 'region': 'Россия'},
    'MOEX.ME': {'name': 'Московская биржа', 'country': 'Россия', 'region': 'Россия'},
    'AFLT.ME': {'name': 'Аэрофлот', 'country': 'Россия', 'region': 'Россия'},

    # Европа
    'SAP.DE': {'name': 'SAP SE', 'country': 'Германия', 'region': 'Европа'},
    'MC.PA': {'name': 'LVMH', 'country': 'Франция', 'region': 'Европа'},
    'NESN.SW': {'name': 'Nestle', 'country': 'Швейцария', 'region': 'Европа'},
    'NOVO-B.CO': {'name': 'Novo Nordisk', 'country': 'Дания', 'region': 'Европа'},
    'ASML.AS': {'name': 'ASML', 'country': 'Нидерланды', 'region': 'Европа'},
    'SIE.DE': {'name': 'Siemens', 'country': 'Германия', 'region': 'Европа'},
    'ULVR.L': {'name': 'Unilever', 'country': 'Великобритания', 'region': 'Европа'},
    'HSBA.L': {'name': 'HSBC', 'country': 'Великобритания', 'region': 'Европа'},
    'RNO.PA': {'name': 'Renault', 'country': 'Франция', 'region': 'Европа'},
    'AIR.PA': {'name': 'Airbus', 'country': 'Франция/Германия', 'region': 'Европа'},
}


CACHE_TTL = 300

DB_NAME = "finance.db"

SVD_N_FACTORS = 50
SVD_N_EPOCHS = 20
SVD_LR = 0.005
SVD_REG = 0.02

TOP_N_RECS = 5