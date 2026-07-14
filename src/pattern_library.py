"""チャート学習ページ用のパターン解説メタデータと、説明用のサンプルデータ生成。

実際の分析ロジック（technical_analysis.py）とは別に、教育目的の
「見た目でわかりやすい」サンプルを手作りで用意する。数値は指標を
正しく再現することではなく、パターンの形を視覚的に伝えることを
優先している。
"""
import numpy as np
import pandas as pd

INDICATOR_PATTERNS = {
    "ma_cross": {
        "name": "MAクロス（ゴールデンクロス）",
        "kind": "buy",
        "summary": "短期移動平均線が長期移動平均線を下から上に抜けたら買いサイン",
        "detail": (
            "短期の移動平均線（MA20など）が長期の移動平均線（MA50など）を"
            "下から上へ突き抜けることを「ゴールデンクロス」と呼び、"
            "上昇トレンドへの転換を示す代表的な買いサインとされます。"
            "逆に上から下へ抜ける「デッドクロス」は売りサインです。"
        ),
    },
    "rsi": {
        "name": "RSI（売られすぎ）",
        "kind": "buy",
        "summary": "RSIが30を下回ったら「売られすぎ」で反発しやすい",
        "detail": (
            "RSI（相対力指数）は0〜100で推移し、一般に30以下は「売られすぎ」、"
            "70以上は「買われすぎ」とされます。売られすぎの水準から反発する"
            "動きは短期的な買いサインとして意識されます。"
        ),
    },
    "macd": {
        "name": "MACDクロス",
        "kind": "buy",
        "summary": "MACD線がシグナル線を下から上に抜けたら買いサイン",
        "detail": (
            "MACD線（短期EMA-長期EMA）がシグナル線（MACD線の平均）を"
            "下から上へ突き抜けると、トレンドが上向きに転じたサインとして"
            "買いが意識されます。ヒストグラム（差分）がマイナスからプラスに"
            "転じる瞬間としても確認できます。"
        ),
    },
    "bb": {
        "name": "ボリンジャーバンド（下限タッチ）",
        "kind": "buy",
        "summary": "株価がバンド下限に接近したら反発を狙う買いサイン",
        "detail": (
            "ボリンジャーバンドは移動平均を中心に±2標準偏差の幅を示します。"
            "統計的に価格の大部分がこの範囲に収まるため、下限バンドへの"
            "接近・タッチは「行き過ぎ」からの反発を狙う買いサインとして"
            "意識されます。上限タッチは逆に売りサインです。"
        ),
    },
    "ichimoku": {
        "name": "一目均衡表（雲抜け）",
        "kind": "buy",
        "summary": "株価が雲（先行スパン帯）を上に抜けたら買いサイン",
        "detail": (
            "一目均衡表の「雲」（先行スパンA・Bで囲まれた帯）は、"
            "抵抗帯・支持帯として機能します。株価が雲を下から上に"
            "抜けると上昇トレンド入りのサイン、雲を上から下に抜けると"
            "下降トレンド入りのサインとされます。"
        ),
    },
    "adx": {
        "name": "ADX（トレンド強度）",
        "kind": "buy",
        "summary": "ADXが25以上かつ+DIが-DIを上回れば強い上昇トレンド",
        "detail": (
            "ADXはトレンドの「強さ」を示す指標で、方向は示しません。"
            "ADXが25以上でトレンドが明確な局面において、+DI（上昇方向の力）が"
            "-DI（下降方向の力）を上回っていれば、強い上昇トレンドが"
            "継続しやすいと判断されます。"
        ),
    },
    "obv": {
        "name": "OBV（出来高の裏付け）",
        "kind": "buy",
        "summary": "OBVがその移動平均を上回れば買い圧力が優勢",
        "detail": (
            "OBV（オンバランスボリューム）は値上がり日の出来高を足し、"
            "値下がり日の出来高を引いて積み上げた指標です。OBVが自身の"
            "移動平均線を上回っている状態は、買い圧力が売り圧力に対して"
            "優勢であることを示唆します。"
        ),
    },
    "vwap": {
        "name": "VWAP（出来高加重平均価格）",
        "kind": "buy",
        "summary": "株価がVWAPを上回っていれば買い優勢の目安",
        "detail": (
            "VWAPは出来高で加重した平均取得価格の目安であり、多くの"
            "参加者の平均コストに近いとされます。株価がVWAPを上回って"
            "推移している間は買い方が優勢、下回っている間は売り方が"
            "優勢と解釈されることが多い指標です。"
        ),
    },
}

CANDLESTICK_PATTERNS = {
    "bullish_marubozu": {
        "name": "陽の丸坊主",
        "kind": "buy",
        "summary": "上下にヒゲがほぼない大陽線。強い買い圧力を示す",
        "detail": (
            "始値がほぼ安値、終値がほぼ高値となる、ヒゲの少ない大きな陽線です。"
            "寄り付きから引けまで一方的に買われたことを示し、強い上昇の"
            "勢いを表すサインとされます。"
        ),
    },
    "bearish_marubozu": {
        "name": "陰の丸坊主",
        "kind": "sell",
        "summary": "上下にヒゲがほぼない大陰線。強い売り圧力を示す",
        "detail": (
            "始値がほぼ高値、終値がほぼ安値となる、ヒゲの少ない大きな陰線です。"
            "寄り付きから引けまで一方的に売られたことを示し、強い下落の"
            "勢いを表すサインとされます。"
        ),
    },
    "doji": {
        "name": "十字線（同事線）",
        "kind": "context",
        "summary": "始値と終値がほぼ同じ。方向感の欠如・転換の予兆",
        "detail": (
            "始値と終値がほぼ同じ水準になり、実体がほとんどない足です。"
            "買いと売りが拮抗していることを示し、トレンドの転換点で"
            "出やすいとされます。単独では方向を示さず、前後の値動きと"
            "合わせて判断します。"
        ),
    },
    "hammer": {
        "name": "ハンマー",
        "kind": "buy",
        "summary": "下降トレンド後の長い下ヒゲ小陽線・小陰線。底打ちサイン",
        "detail": (
            "下降トレンドの後に出現する、下ヒゲが実体の2倍以上ある"
            "小さな実体の足です。一度大きく売られたものの引けにかけて"
            "買い戻された形で、底打ち・反発のサインとされます。"
        ),
    },
    "hanging_man": {
        "name": "首吊り線",
        "kind": "sell",
        "summary": "上昇トレンド後の長い下ヒゲ小陽線・小陰線。天井サイン",
        "detail": (
            "ハンマーと同じ形（長い下ヒゲの小さな実体）ですが、"
            "上昇トレンドの後に出現した場合はこう呼ばれ、天井圏での"
            "売り圧力の高まりを示す反落サインとされます。"
        ),
    },
    "bullish_engulfing": {
        "name": "陽の包み足",
        "kind": "buy",
        "summary": "前日の陰線を丸ごと包む陽線。強い買い転換サイン",
        "detail": (
            "前日の陰線の実体を、当日の陽線の実体が始値から終値まで"
            "完全に包み込む形です。売り優勢だった流れが一気に買いへ"
            "転じたことを示し、底値圏で出ると強い反転サインとされます。"
        ),
    },
    "bearish_engulfing": {
        "name": "陰の包み足",
        "kind": "sell",
        "summary": "前日の陽線を丸ごと包む陰線。強い売り転換サイン",
        "detail": (
            "前日の陽線の実体を、当日の陰線の実体が完全に包み込む形です。"
            "買い優勢だった流れが一気に売りへ転じたことを示し、高値圏で"
            "出ると強い反転サインとされます。"
        ),
    },
}


def generate_indicator_example(key: str) -> dict:
    """指標パターンの説明用サンプルデータ（線グラフ用）を返す。
    実際の指標計算とは独立した、見た目重視の手作りデータ。"""
    n = 40
    x = list(range(n))

    if key == "ma_cross":
        short = [50 - i * 0.6 for i in range(20)] + [38 + (i - 19) * 1.4 for i in range(20, n)]
        long = [50 - i * 0.25 for i in range(n)]
        return {"kind": "dual_line", "x": x, "primary": short, "secondary": long,
                "primary_name": "短期MA", "secondary_name": "長期MA"}

    if key == "rsi":
        vals = [70 - i * 2.8 for i in range(15)] + [28 + (i - 14) * 3.5 for i in range(15, n)]
        vals = [max(5, min(95, v)) for v in vals]
        return {"kind": "oscillator", "x": x, "primary": vals, "primary_name": "RSI",
                "zone_low": 30, "zone_high": 70}

    if key == "macd":
        signal = [np.sin(i / 6) * 3 for i in range(n)]
        macd_line = [s - 2.5 + (i / n) * 5 for i, s in enumerate(signal)]
        return {"kind": "dual_line", "x": x, "primary": macd_line, "secondary": signal,
                "primary_name": "MACD線", "secondary_name": "シグナル線"}

    if key == "bb":
        mid = [50] * n
        upper = [55] * n
        lower = [45] * n
        price = [50 - abs(np.sin(i / 5)) * 4 for i in range(25)] + [46 + (i - 24) * 0.6 for i in range(25, n)]
        return {"kind": "band", "x": x, "primary": price, "band_upper": upper, "band_lower": lower,
                "primary_name": "株価", "band_name": "ボリンジャーバンド"}

    if key == "ichimoku":
        cloud_top = [50 + np.sin(i / 8) * 2 for i in range(n)]
        cloud_bottom = [c - 3 for c in cloud_top]
        price = [46 - i * 0.15 for i in range(20)] + [43 + (i - 19) * 0.9 for i in range(20, n)]
        return {"kind": "band", "x": x, "primary": price, "band_upper": cloud_top, "band_lower": cloud_bottom,
                "primary_name": "株価", "band_name": "雲（先行スパンA/B）"}

    if key == "adx":
        adx = [15 + i * 0.6 for i in range(n)]
        plus_di = [20 + i * 0.7 for i in range(n)]
        minus_di = [30 - i * 0.4 for i in range(n)]
        return {"kind": "adx", "x": x, "adx": adx, "plus_di": plus_di, "minus_di": minus_di}

    if key == "obv":
        ema = [50 + i * 0.3 for i in range(n)]
        obv = [50 - i * 0.1 for i in range(22)] + [47.6 + (i - 21) * 1.1 for i in range(22, n)]
        return {"kind": "dual_line", "x": x, "primary": obv, "secondary": ema,
                "primary_name": "OBV", "secondary_name": "OBVの移動平均"}

    if key == "vwap":
        vwap = [50 + np.sin(i / 10) * 1.5 for i in range(n)]
        price = [48 - i * 0.1 for i in range(22)] + [45.8 + (i - 21) * 0.8 for i in range(22, n)]
        return {"kind": "dual_line", "x": x, "primary": price, "secondary": vwap,
                "primary_name": "株価", "secondary_name": "VWAP"}

    raise ValueError(f"unknown indicator pattern: {key}")


def generate_candlestick_example(key: str) -> pd.DataFrame:
    """ローソク足パターンの説明用サンプルOHLCデータ（7本）を返す。
    末尾2本が判定ロジック（technical_analysis.detect_candlestick_patterns）で
    実際にそのパターンとして検出されることを確認済みの値。"""
    dates = pd.date_range("2026-01-01", periods=7, freq="D")

    # 6本の下降トレンド（反転系パターンの「前提」として使う）
    base_down = [
        (112, 113, 110, 111), (111, 111.5, 108, 109), (109, 109.5, 106, 107),
        (107, 107.5, 104, 105), (105, 105.5, 102, 103), (103, 103.5, 100, 101),
    ]
    # 6本の上昇トレンド
    base_up = [
        (90, 91.5, 89, 91), (91, 92.5, 90.5, 93), (93, 94.5, 92.5, 95),
        (95, 96.5, 94.5, 97), (97, 98.5, 96.5, 99), (99, 100.5, 98.5, 101),
    ]

    if key == "bullish_marubozu":
        rows = base_down[:-1] + [(103, 103.5, 100, 101), (101, 108, 100.8, 107.8)]
    elif key == "bearish_marubozu":
        rows = base_up[:-1] + [(99, 100.5, 98.5, 101), (101, 101.2, 94, 94.3)]
    elif key == "doji":
        rows = base_down[:-1] + [(103, 103.5, 100, 101), (101, 104, 98, 101.2)]
    elif key == "hammer":
        rows = base_down + [(99.3, 100, 95, 100)]
    elif key == "hanging_man":
        rows = base_up + [(99.3, 100, 95, 100)]
    elif key == "bullish_engulfing":
        rows = base_down + [(100.5, 104.3, 100.3, 104)]
    elif key == "bearish_engulfing":
        rows = base_up + [(101.5, 101.7, 98.3, 98.5)]
    else:
        raise ValueError(f"unknown candlestick pattern: {key}")

    df = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=dates)
    return df
