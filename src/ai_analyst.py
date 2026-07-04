import pandas as pd
import ollama
from typing import Generator, NamedTuple

from src.gemini_client import GEMINI_MODELS, is_available as gemini_available, stream_gemini


class ModelChoice(NamedTuple):
    provider: str  # "ollama" or "gemini"
    name: str


def list_ollama_models() -> list[str]:
    try:
        names = [m.model for m in ollama.list().models]
        return names or ["gemma4:12b"]
    except Exception:
        return ["gemma4:12b"]


def ollama_reachable() -> bool:
    try:
        ollama.list()
        return True
    except Exception:
        return False


def list_model_choices() -> list[ModelChoice]:
    choices = []
    if ollama_reachable():
        choices += [ModelChoice("ollama", m) for m in list_ollama_models()]
    if gemini_available():
        choices += [ModelChoice("gemini", m) for m in GEMINI_MODELS]
    return choices


def _fmt(v, decimals: int = 2) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "N/A"
    return f"{v:,.{decimals}f}"


def _fmt_pct(v) -> str:
    if v is None:
        return "N/A"
    arrow = "▲" if v >= 0 else "▼"
    return f"{arrow}{abs(v):.2f}%"


def _build_prompt(df: pd.DataFrame, info: dict, signals: dict, stats: dict) -> str:
    ticker = info.get("symbol", "不明")
    name = info.get("longName") or info.get("shortName") or ticker
    currency = info.get("currency", "")
    sector = info.get("sector", "不明")
    industry = info.get("industry", "")

    current = df["close"].iloc[-1]
    last = df.iloc[-1]

    low52 = stats.get("week52_low", current)
    high52 = stats.get("week52_high", current)
    range52 = high52 - low52
    pos52 = (current - low52) / range52 * 100 if range52 > 0 else 50.0

    avg_vol = stats.get("avg_volume", 0)
    cur_vol = stats.get("current_volume", 0)
    vol_ratio = cur_vol / avg_vol * 100 if avg_vol > 0 else 100.0

    return f"""あなたは10年以上の経験を持つプロの株式アナリストです。以下のデータをもとに、具体的な数値を交えた詳細な分析レポートを日本語で作成してください。

## 銘柄情報
- 銘柄名: {name}
- ティッカー: {ticker}
- セクター: {sector} / {industry}
- 通貨: {currency}
- 現在価格: {_fmt(current, 0)} {currency}

## 価格パフォーマンス
| 期間 | リターン |
|------|--------|
| 1週間 | {_fmt_pct(stats.get('return_1w'))} |
| 1ヶ月 | {_fmt_pct(stats.get('return_1m'))} |
| 3ヶ月 | {_fmt_pct(stats.get('return_3m'))} |
| 1年 | {_fmt_pct(stats.get('return_1y'))} |

- 52週高値: {_fmt(high52, 0)} {currency}
- 52週安値: {_fmt(low52, 0)} {currency}
- 52週レンジ内ポジション: {_fmt(pos52, 1)}%（0%=最安値、100%=最高値）
- 年率ボラティリティ: {_fmt(stats.get('volatility'))}%

## テクニカル指標（最新値）
- MA20: {_fmt(last.get('ma20'), 0)} {currency}（現在値との乖離: {_fmt((current / last.get('ma20', current) - 1) * 100 if last.get('ma20') else 0, 2)}%）
- MA50: {_fmt(last.get('ma50'), 0)} {currency}（現在値との乖離: {_fmt((current / last.get('ma50', current) - 1) * 100 if last.get('ma50') else 0, 2)}%）
- MA200: {_fmt(last.get('ma200'), 0)} {currency}（現在値との乖離: {_fmt((current / last.get('ma200', current) - 1) * 100 if last.get('ma200') else 0, 2)}%）
- RSI(14): {_fmt(last.get('rsi'))}
- MACD: {_fmt(last.get('macd'))} / シグナル: {_fmt(last.get('macd_signal'))} / ヒスト: {_fmt(last.get('macd_hist'))}
- ボリンジャーバンド上限: {_fmt(last.get('bb_upper'), 0)} / 下限: {_fmt(last.get('bb_lower'), 0)} {currency}
- 一目均衡表 転換線: {_fmt(last.get('ichimoku_tenkan'), 0)} / 基準線: {_fmt(last.get('ichimoku_kijun'), 0)} / 先行スパンA: {_fmt(last.get('ichimoku_senkou_a'), 0)} / 先行スパンB: {_fmt(last.get('ichimoku_senkou_b'), 0)}
- ADX: {_fmt(last.get('adx'), 1)}（+DI: {_fmt(last.get('plus_di'), 1)} / -DI: {_fmt(last.get('minus_di'), 1)}）
- OBV: {_fmt(last.get('obv'), 0)} / OBV EMA20: {_fmt(last.get('obv_ema'), 0)}
- VWAP(20日): {_fmt(last.get('vwap'), 0)} {currency}

## シグナル判定
- MAクロス: {signals.get('ma_cross', 'N/A')}
- RSI: {signals.get('rsi', 'N/A')}
- MACD: {signals.get('macd', 'N/A')}
- ボリンジャーバンド: {signals.get('bb', 'N/A')}
- 一目均衡表（雲との位置関係）: {signals.get('ichimoku', 'N/A')}
- ADX（トレンド強度・方向）: {signals.get('adx', 'N/A')}
- OBV（出来高の裏付け）: {signals.get('obv', 'N/A')}
- VWAP（20日出来高加重平均価格との乖離）: {signals.get('vwap', 'N/A')}
- **総合シグナル: {signals.get('overall', 'N/A')}**

## 出来高
- 直近出来高: {int(cur_vol):,}
- 20日平均: {int(avg_vol):,}
- 平均比: {_fmt(vol_ratio, 1)}%

---

以下の形式で分析レポートを作成してください：

### 1. 現状分析
現在の価格水準、トレンドの方向性、重要なサポート・レジスタンスラインを分析してください。

### 2. テクニカル分析
各指標（MA、RSI、MACD、ボリンジャーバンド）が示すシグナルを解説し、それらが総合的に何を意味するか説明してください。

### 3. 短期見通し（1〜3ヶ月）
短期的な価格動向の予測と、その根拠を具体的な価格帯とともに示してください。

### 4. 中長期見通し（6ヶ月〜1年）
中長期の成長可能性と期待リターンの目安（パーセンテージ）を示してください。

### 5. 具体的な戦略
**買い場の目安:**
- 推奨エントリー価格帯または条件

**売り場の目安（利益確定）:**
- 目標価格帯または条件

**損切りライン:**
- リスク管理のための損切り価格の目安

### 6. 注意すべきリスク
この銘柄に特有のリスク要因を3点挙げてください。

### 7. 総合評価
「強い買い」「買い」「中立」「売り」「強い売り」のいずれかで評価し、その理由を2〜3文で述べてください。

※ 本分析はテクニカル指標のみに基づいており、ファンダメンタルズ分析は含まれません。投資は自己責任でお願いします。
"""


def analyze_stock_stream(
    df: pd.DataFrame,
    info: dict,
    signals: dict,
    stats: dict,
    model: ModelChoice,
) -> Generator[str, None, None]:
    prompt = _build_prompt(df, info, signals, stats)

    if model.provider == "gemini":
        try:
            yield from stream_gemini(prompt, model.name)
        except Exception as e:
            yield f"\n\n**エラーが発生しました**\n\n```\n{e}\n```\n\nGemini APIキー（.envのGEMINI_API_KEY）が正しく設定されているか確認してください。"
        return

    try:
        stream = ollama.chat(
            model=model.name,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield content
    except Exception as e:
        yield f"\n\n**エラーが発生しました**\n\n```\n{e}\n```\n\nOllamaが起動していることを確認してください: `ollama serve`"
