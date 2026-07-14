import pandas as pd
import numpy as np

DIRECTIONAL_SIGNAL_KEYS = [
    "ma_cross", "rsi", "macd", "bb", "ichimoku", "adx", "obv", "vwap",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    high, low, close, volume = df["high"], df["low"], df["close"], df["volume"]

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

    _add_ichimoku(df, high, low, close)
    _add_adx(df, high, low, close)
    df["obv"] = _calc_obv(close, volume)
    df["obv_ema"] = df["obv"].ewm(span=20, adjust=False).mean()
    df["vwap"] = _calc_vwap(high, low, close, volume)

    return df


def _calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _add_ichimoku(df: pd.DataFrame, high: pd.Series, low: pd.Series, close: pd.Series) -> None:
    tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
    kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
    senkou_a_raw = (tenkan + kijun) / 2
    senkou_b_raw = (high.rolling(52).max() + low.rolling(52).min()) / 2

    df["ichimoku_tenkan"] = tenkan
    df["ichimoku_kijun"] = kijun
    # 先行スパンは26日先に投影されるのが本来の表示だが、シグナル判定用に
    # 「今日時点で有効な雲」を得るため過去方向にシフトして保持する
    df["ichimoku_senkou_a"] = senkou_a_raw.shift(26)
    df["ichimoku_senkou_b"] = senkou_b_raw.shift(26)
    df["ichimoku_senkou_a_raw"] = senkou_a_raw
    df["ichimoku_senkou_b_raw"] = senkou_b_raw
    df["ichimoku_chikou"] = close.shift(-26)


def _add_adx(df: pd.DataFrame, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> None:
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)

    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=df.index)

    atr = tr.ewm(alpha=1 / period, adjust=False).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)

    df["plus_di"] = plus_di
    df["minus_di"] = minus_di
    df["adx"] = dx.ewm(alpha=1 / period, adjust=False).mean()


def _calc_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()


def _calc_vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, period: int = 20) -> pd.Series:
    typical_price = (high + low + close) / 3
    pv = typical_price * volume
    return pv.rolling(period).sum() / volume.rolling(period).sum()


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

    senkou_a = last.get("ichimoku_senkou_a")
    senkou_b = last.get("ichimoku_senkou_b")
    if senkou_a is not None and senkou_b is not None and not pd.isna(senkou_a) and not pd.isna(senkou_b):
        cloud_top = max(senkou_a, senkou_b)
        cloud_bottom = min(senkou_a, senkou_b)
        if close > cloud_top:
            signals["ichimoku"] = "買い"
        elif close < cloud_bottom:
            signals["ichimoku"] = "売り"
        else:
            signals["ichimoku"] = "中立"
    else:
        signals["ichimoku"] = "中立"

    adx = last.get("adx")
    plus_di = last.get("plus_di")
    minus_di = last.get("minus_di")
    if adx is not None and not pd.isna(adx) and not pd.isna(plus_di) and not pd.isna(minus_di):
        if adx >= 25 and plus_di > minus_di:
            signals["adx"] = "買い"
        elif adx >= 25 and minus_di > plus_di:
            signals["adx"] = "売り"
        else:
            signals["adx"] = "中立"
    else:
        signals["adx"] = "中立"

    obv = last.get("obv")
    obv_ema = last.get("obv_ema")
    if obv is not None and obv_ema is not None and not pd.isna(obv) and not pd.isna(obv_ema):
        signals["obv"] = "買い" if obv > obv_ema else "売り" if obv < obv_ema else "中立"
    else:
        signals["obv"] = "中立"

    vwap = last.get("vwap")
    if vwap is not None and not pd.isna(vwap):
        signals["vwap"] = "買い" if close > vwap else "売り" if close < vwap else "中立"
    else:
        signals["vwap"] = "中立"

    buy = sum(1 for k in DIRECTIONAL_SIGNAL_KEYS if signals[k] == "買い")
    sell = sum(1 for k in DIRECTIONAL_SIGNAL_KEYS if signals[k] == "売り")
    total = len(DIRECTIONAL_SIGNAL_KEYS)

    if buy / total >= 0.75:
        signals["overall"] = "買い"
    elif sell / total >= 0.75:
        signals["overall"] = "売り"
    elif buy > sell:
        signals["overall"] = "やや買い"
    elif sell > buy:
        signals["overall"] = "やや売り"
    else:
        signals["overall"] = "中立"

    return signals


CANDLESTICK_PATTERN_KEYS = [
    "bullish_marubozu", "bearish_marubozu", "doji",
    "hammer", "hanging_man", "bullish_engulfing", "bearish_engulfing",
]


def detect_candlestick_patterns(df: pd.DataFrame) -> dict:
    """直近1本のローソク足に、代表的なローソク足パターンが出現しているかを判定する。
    trueになっているキーが1つもない場合は「該当パターンなし」を意味する。"""
    result = {key: False for key in CANDLESTICK_PATTERN_KEYS}
    if len(df) < 7:
        return result

    last = df.iloc[-1]
    prev = df.iloc[-2]
    o, h, l, c = last["open"], last["high"], last["low"], last["close"]
    po, pc = prev["open"], prev["close"]

    rng = h - l
    if rng <= 0 or any(pd.isna(v) for v in (o, h, l, c, po, pc)):
        return result

    body = abs(c - o)
    upper_wick = h - max(o, c)
    lower_wick = min(o, c) - l
    is_bullish = c > o
    is_bearish = c < o

    result["bullish_marubozu"] = is_bullish and body >= 0.9 * rng
    result["bearish_marubozu"] = is_bearish and body >= 0.9 * rng
    result["doji"] = body <= 0.1 * rng

    # 直近5本の値動きでトレンド方向を判定し、同じ形でも
    # 下降トレンド後なら「ハンマー」、上昇トレンド後なら「首吊り線」と区別する
    prior_trend = df["close"].iloc[-2] - df["close"].iloc[-7]
    is_small_body_bottom = body > 0 and lower_wick >= 2 * body and upper_wick <= 0.3 * body
    if is_small_body_bottom and prior_trend < 0:
        result["hammer"] = True
    if is_small_body_bottom and prior_trend > 0:
        result["hanging_man"] = True

    prev_is_bearish = pc < po
    prev_is_bullish = pc > po
    result["bullish_engulfing"] = is_bullish and prev_is_bearish and o <= pc and c >= po
    result["bearish_engulfing"] = is_bearish and prev_is_bullish and o >= pc and c <= po

    return result


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
