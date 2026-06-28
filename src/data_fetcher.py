import yfinance as yf
import pandas as pd


def get_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame | None:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df is None or df.empty:
            return None
        df.columns = [c.lower() for c in df.columns]
        df.index = pd.to_datetime(df.index)
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        return df
    except Exception as e:
        print(f"データ取得エラー ({ticker}): {e}")
        return None


def get_stock_info(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info if info else {}
    except Exception:
        return {}
