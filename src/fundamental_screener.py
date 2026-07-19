import yfinance as yf
from yfinance import EquityQuery

from src.sectors import SECTOR_JA

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
    pbr_min: float | None = None,
    pbr_max: float | None = None,
    div_yield_min: float | None = None,
    div_yield_max: float | None = None,
    sector_ja: str | None = None,
    size: int = 50,
) -> dict:
    """yfinanceの公式スクリーニングAPI（Yahoo!ファイナンスの正規データ）で、
    地域・時価総額・売上高・PER・ROE・PBR・配当利回り・セクターの条件に合う
    銘柄を検索する。スクレイピングではないため、株探/IR BANK等のような
    ボット判定ブロックの心配がない。戻り値は {"total": 該当件数, "quotes": [...]}。"""
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
    if pbr_min is not None:
        conditions.append(EquityQuery("gt", ["pricebookratio.quarterly", pbr_min]))
    if pbr_max is not None:
        conditions.append(EquityQuery("lt", ["pricebookratio.quarterly", pbr_max]))
    if div_yield_min is not None:
        conditions.append(EquityQuery("gt", ["forward_dividend_yield", div_yield_min]))
    if div_yield_max is not None:
        conditions.append(EquityQuery("lt", ["forward_dividend_yield", div_yield_max]))
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


def get_sector_performance(region: str, sample_size: int = 10) -> list[dict]:
    """セクターごとに時価総額上位銘柄をサンプリングし、当日の値動き
    （regularMarketChangePercent）の単純平均をセクターの参考騰落率として返す。
    yfinanceにセクター指数そのものは無いため、代表銘柄群の平均で近似する簡易指標。
    戻り値は騰落率の高い順にソートした
    [{"sector_ja": str, "avg_change_pct": float, "count": int}, ...]。"""
    results = []
    for sector_ja in SECTOR_JA.values():
        quotes = screen_stocks(region=region, sector_ja=sector_ja, size=sample_size)["quotes"]
        changes = [
            q.get("regularMarketChangePercent") for q in quotes
            if q.get("regularMarketChangePercent") is not None
        ]
        if not changes:
            continue
        results.append({
            "sector_ja": sector_ja,
            "avg_change_pct": sum(changes) / len(changes),
            "count": len(changes),
        })
    results.sort(key=lambda r: r["avg_change_pct"], reverse=True)
    return results
