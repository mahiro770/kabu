import pandas as pd
import numpy as np


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    close = df["close"]

    df["ma20"] = close.rolling(20).mean()
    df["ma50"] = close.rolling(50).mean()
    df["ma200"] = close.rolling(200).mean()

    df["bb_mid"] = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    df["bb_upper"] = df["bb_mid"] + 2 * bb_std
    df["bb_lower"] = df["bb_mid"] - 2 * bb_std

    df["rsi"] = _calc_rsi(close, 14)

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    return df


def _calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def get_signals(df: pd.DataFrame) -> dict:
    signals = {}
    last = df.iloc[-1]

    ma20 = last.get("ma20")
    ma50 = last.get("ma50")
    if ma20 is not None and ma50 is not None and not pd.isna(ma20) and not pd.isna(ma50):
        signals["ma_cross"] = "買い" if ma20 > ma50 else "売り" if ma20 < ma50 else "中立"
    else:
        signals["ma_cross"] = "中立"

    rsi = last.get("rsi")
    if rsi is not None and not pd.isna(rsi):
        if rsi < 30:
            signals["rsi"] = "買い"
        elif rsi > 70:
            signals["rsi"] = "売り"
        else:
            signals["rsi"] = "中立"
    else:
        signals["rsi"] = "中立"

    macd = last.get("macd")
    macd_sig = last.get("macd_signal")
    if macd is not None and macd_sig is not None and not pd.isna(macd) and not pd.isna(macd_sig):
        signals["macd"] = "買い" if macd > macd_sig else "売り" if macd < macd_sig else "中立"
    else:
        signals["macd"] = "中立"

    bb_upper = last.get("bb_upper")
    bb_lower = last.get("bb_lower")
    close = last.get("close")
    if bb_upper is not None and bb_lower is not None and not pd.isna(bb_upper) and not pd.isna(bb_lower):
        bb_range = bb_upper - bb_lower
        bb_pos = (close - bb_lower) / bb_range if bb_range > 0 else 0.5
        if bb_pos < 0.2:
            signals["bb"] = "買い"
        elif bb_pos > 0.8:
            signals["bb"] = "売り"
        else:
            signals["bb"] = "中立"
    else:
        signals["bb"] = "中立"

    buy = sum(1 for s in signals.values() if s == "買い")
    sell = sum(1 for s in signals.values() if s == "売り")

    if buy >= 3:
        signals["overall"] = "買い"
    elif sell >= 3:
        signals["overall"] = "売り"
    elif buy > sell:
        signals["overall"] = "やや買い"
    elif sell > buy:
        signals["overall"] = "やや売り"
    else:
        signals["overall"] = "中立"

    return signals


def get_summary_stats(df: pd.DataFrame, info: dict) -> dict:
    stats = {}
    current = df["close"].iloc[-1]

    stats["week52_high"] = df["high"].max()
    stats["week52_low"] = df["low"].min()

    def safe_return(days: int):
        idx = min(days, len(df) - 1)
        if idx <= 0:
            return None
        past = df["close"].iloc[-idx]
        return (current - past) / past * 100

    stats["return_1w"] = safe_return(5)
    stats["return_1m"] = safe_return(21)
    stats["return_3m"] = safe_return(63)
    stats["return_1y"] = safe_return(252)

    stats["avg_volume"] = float(df["volume"].rolling(20).mean().iloc[-1])
    stats["current_volume"] = float(df["volume"].iloc[-1])

    daily_returns = df["close"].pct_change().dropna()
    stats["volatility"] = float(daily_returns.std() * (252 ** 0.5) * 100)

    return stats
