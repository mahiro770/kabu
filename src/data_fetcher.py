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


def get_earnings_forecast(ticker: str) -> dict | None:
    """アナリストによる今期・来期の業績予想と目標株価を取得する。"""
    try:
        stock = yf.Ticker(ticker)
        earnings_est = stock.earnings_estimate
        revenue_est = stock.revenue_estimate
        price_targets = stock.analyst_price_targets
        has_earnings = earnings_est is not None and not earnings_est.empty
        has_revenue = revenue_est is not None and not revenue_est.empty
        if not has_earnings and not has_revenue and not price_targets:
            return None
        return {
            "earnings_estimate": earnings_est if has_earnings else None,
            "revenue_estimate": revenue_est if has_revenue else None,
            "price_targets": price_targets or None,
        }
    except Exception as e:
        print(f"業績予想データ取得エラー ({ticker}): {e}")
        return None


def get_major_holders(ticker: str) -> list[dict] | None:
    """機関投資家の保有比率上位を取得する（主に米国株向け）。"""
    try:
        stock = yf.Ticker(ticker)
        holders = stock.institutional_holders
        if holders is None or holders.empty:
            return None
        holders = holders.sort_values("pctHeld", ascending=False)
        return [
            {
                "name": row.get("Holder"),
                "pct": row.get("pctHeld"),
                "shares": row.get("Shares"),
                "value": row.get("Value"),
            }
            for _, row in holders.head(10).iterrows()
        ]
    except Exception as e:
        print(f"大株主データ取得エラー ({ticker}): {e}")
        return None


def get_financial_history(ticker: str) -> pd.DataFrame | None:
    """過去数年分の売上高・営業利益・純利益・自己資本比率を年度別に取得する。"""
    try:
        stock = yf.Ticker(ticker)
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        if financials is None or financials.empty:
            return None

        rows = []
        for year in financials.columns:
            revenue = financials.loc["Total Revenue", year] if "Total Revenue" in financials.index else None
            if revenue is None or pd.isna(revenue):
                continue

            operating_income = (
                financials.loc["Operating Income", year]
                if "Operating Income" in financials.index else None
            )
            net_income = financials.loc["Net Income", year] if "Net Income" in financials.index else None

            equity_ratio = None
            if balance_sheet is not None and year in balance_sheet.columns:
                equity = (
                    balance_sheet.loc["Stockholders Equity", year]
                    if "Stockholders Equity" in balance_sheet.index else None
                )
                assets = balance_sheet.loc["Total Assets", year] if "Total Assets" in balance_sheet.index else None
                if equity is not None and assets and not pd.isna(equity) and not pd.isna(assets):
                    equity_ratio = equity / assets

            rows.append({
                "year": year,
                "revenue": revenue,
                "operating_income": operating_income,
                "net_income": net_income,
                "equity_ratio": equity_ratio,
            })

        if not rows:
            return None
        return pd.DataFrame(rows).sort_values("year", ascending=False).reset_index(drop=True)
    except Exception as e:
        print(f"財務推移データ取得エラー ({ticker}): {e}")
        return None
