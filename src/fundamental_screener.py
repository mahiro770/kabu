import yfinance as yf
from yfinance import EquityQuery

REGION_JP = "jp"
REGION_US = "us"

SECTOR_EN = {
    "情報技術": "Technology",
    "ヘルスケア": "Healthcare",
    "金融サービス": "Financial Services",
    "一般消費財・サービス": "Consumer Cyclical",
    "生活必需品": "Consumer Defensive",
    "資本財・サービス": "Industrials",
    "エネルギー": "Energy",
    "素材": "Basic Materials",
    "公益事業": "Utilities",
    "不動産": "Real Estate",
    "コミュニケーション・サービス": "Communication Services",
}


def screen_stocks(
    region: str,
    market_cap_min: float | None = None,
    market_cap_max: float | None = None,
    revenue_min: float | None = None,
    revenue_max: float | None = None,
    per_min: float | None = None,
    per_max: float | None = None,
    roe_min: float | None = None,
    roe_max: float | None = None,
    sector_ja: str | None = None,
    size: int = 50,
) -> dict:
    """yfinanceの公式スクリーニングAPI（Yahoo!ファイナンスの正規データ）で、
    地域・時価総額・売上高・PER・ROE・セクターの条件に合う銘柄を検索する。
    スクレイピングではないため、株探/IR BANK等のようなボット判定ブロックの
    心配がない。戻り値は {"total": 該当件数, "quotes": [...]}。"""
    conditions = [EquityQuery("eq", ["region", region])]

    if market_cap_min is not None:
        conditions.append(EquityQuery("gt", ["intradaymarketcap", market_cap_min]))
    if market_cap_max is not None:
        conditions.append(EquityQuery("lt", ["intradaymarketcap", market_cap_max]))
    if revenue_min is not None:
        conditions.append(EquityQuery("gt", ["totalrevenues.lasttwelvemonths", revenue_min]))
    if revenue_max is not None:
        conditions.append(EquityQuery("lt", ["totalrevenues.lasttwelvemonths", revenue_max]))
    if per_min is not None:
        conditions.append(EquityQuery("gt", ["peratio.lasttwelvemonths", per_min]))
    if per_max is not None:
        conditions.append(EquityQuery("lt", ["peratio.lasttwelvemonths", per_max]))
    if roe_min is not None:
        conditions.append(EquityQuery("gt", ["returnonequity.lasttwelvemonths", roe_min]))
    if roe_max is not None:
        conditions.append(EquityQuery("lt", ["returnonequity.lasttwelvemonths", roe_max]))
    if sector_ja:
        sector_en = SECTOR_EN.get(sector_ja)
        if sector_en:
            conditions.append(EquityQuery("eq", ["sector", sector_en]))

    query = EquityQuery("and", conditions) if len(conditions) > 1 else conditions[0]
    try:
        resp = yf.screen(query, size=size, sortField="intradaymarketcap", sortAsc=False)
    except Exception as e:
        print(f"スクリーニングエラー: {e}")
        return {"total": 0, "quotes": []}
    return {"total": resp.get("total", 0), "quotes": resp.get("quotes", [])}
