import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Shared palette — mirrors the tokens in src/ui.py and landing/DESIGN.md so
# charts, badges and the surrounding chrome all read as one system.
_UP = "#4E9A79"       # bullish / buy
_DOWN = "#C05B3F"      # bearish / sell
_GOLD = "#D2AE5C"      # single accent, used for the "featured" line in a chart
_INK = "#EDEAE0"
_INK_SOFT = "#A6A399"
_CLAY = "#B8834F"      # short-term reference line (MA20 / Tenkan-sen)
_STONE = "#7C8A94"     # mid-term reference line (MA50 / Kijun-sen / MACD / OBV EMA)
_MAUVE = "#8D7BA3"     # long-term / lagging reference line (MA200 / Chikou Span)
_HAIRLINE = "rgba(237,234,224,0.14)"
_HAIRLINE_STRONG = "rgba(237,234,224,0.28)"

_TRANSPARENT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=_INK_SOFT),
)


def _add_ichimoku_traces(fig: go.Figure, df: pd.DataFrame, ja: bool = True) -> None:
    fig.add_trace(
        go.Scatter(x=df.index, y=df["ichimoku_tenkan"], name="転換線" if ja else "Tenkan-sen",
                   line=dict(color=_CLAY, width=1)),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["ichimoku_kijun"], name="基準線" if ja else "Kijun-sen",
                   line=dict(color=_STONE, width=1)),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["ichimoku_chikou"], name="遅行スパン" if ja else "Chikou Span",
                   line=dict(color=_MAUVE, width=1, dash="dot")),
        row=1, col=1,
    )

    # 先行スパンA/Bは26日先に投影して雲として表示する（未来分は日付を延長）
    future_dates = pd.bdate_range(start=df.index[-1] + pd.Timedelta(days=1), periods=26)
    cloud_index = df.index.append(future_dates)

    senkou_a = pd.concat([df["ichimoku_senkou_a"], df["ichimoku_senkou_a_raw"].iloc[-26:].set_axis(future_dates)])
    senkou_b = pd.concat([df["ichimoku_senkou_b"], df["ichimoku_senkou_b_raw"].iloc[-26:].set_axis(future_dates)])
    senkou_a = senkou_a.reindex(cloud_index)
    senkou_b = senkou_b.reindex(cloud_index)

    fig.add_trace(
        go.Scatter(x=cloud_index, y=senkou_b, name="先行スパンB" if ja else "Senkou Span B",
                   line=dict(color="rgba(192,91,63,0.4)", width=1)),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=cloud_index, y=senkou_a, name="先行スパンA（雲）" if ja else "Senkou Span A (Cloud)",
                   line=dict(color="rgba(78,154,121,0.4)", width=1),
                   fill="tonexty", fillcolor="rgba(166,163,153,0.14)"),
        row=1, col=1,
    )


def build_watchlist_line_chart(close: pd.Series, color: str, intraday: bool = False) -> go.Figure:
    """ウォッチリスト一覧用の軸・日付ラベル付き価格チャート。"""
    tick_fmt = "%H:%M" if intraday else "%m/%d"
    fig = go.Figure(go.Scatter(
        x=close.index, y=close.values, mode="lines", line=dict(color=color, width=1.5),
        hovertemplate=f"%{{x|%Y/%m/%d {'%H:%M' if intraday else ''}}}<br>%{{y:,.1f}}<extra></extra>",
    ))
    fig.update_layout(
        margin=dict(l=4, r=48, t=8, b=24),
        height=160,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=False, tickformat=tick_fmt, nticks=5,
            tickfont=dict(size=10, color=_INK_SOFT), fixedrange=True,
        ),
        yaxis=dict(
            side="right", showgrid=True, gridcolor=_HAIRLINE, griddash="dash",
            tickfont=dict(size=10, color=_INK_SOFT), fixedrange=True,
        ),
    )
    return fig


def build_sidebar_sparkline(close: pd.Series, color: str) -> go.Figure:
    """サイドバーの簡易ウォッチリスト用の日付軸・価格帯付きミニチャート。"""
    fig = go.Figure(go.Scatter(
        x=close.index, y=close.values, mode="lines", line=dict(color=color, width=1.5),
        hovertemplate="%{x|%m/%d}<br>%{y:,.1f}<extra></extra>",
    ))
    fig.update_layout(
        margin=dict(l=0, r=36, t=4, b=18),
        height=54,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            visible=True, showgrid=False, tickformat="%m/%d", nticks=3,
            tickfont=dict(size=9, color=_INK), fixedrange=True,
        ),
        yaxis=dict(
            visible=True, side="right", showgrid=True, gridcolor=_HAIRLINE,
            griddash="dash", nticks=3, tickfont=dict(size=9, color=_INK_SOFT), fixedrange=True,
        ),
    )
    return fig


_PATTERN_LAYOUT = dict(
    margin=dict(l=8, r=8, t=8, b=8),
    height=180,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                font=dict(size=10, color=_INK_SOFT)),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(visible=False, fixedrange=True),
    yaxis=dict(visible=False, fixedrange=True),
)


def build_pattern_example_chart(data: dict) -> go.Figure:
    """チャート学習ページ用の、指標パターンの見た目を伝えるための簡易ライン図。"""
    kind = data["kind"]
    x = data["x"]

    if kind == "dual_line":
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=data["primary"], mode="lines", name=data["primary_name"],
                                  line=dict(color=_UP, width=2)))
        fig.add_trace(go.Scatter(x=x, y=data["secondary"], mode="lines", name=data["secondary_name"],
                                  line=dict(color=_INK_SOFT, width=1.5, dash="dot")))
        fig.update_layout(**_PATTERN_LAYOUT)
        return fig

    if kind == "oscillator":
        fig = go.Figure()
        fig.add_hrect(y0=0, y1=data["zone_low"], fillcolor=_UP, opacity=0.12, line_width=0)
        fig.add_hrect(y0=data["zone_high"], y1=100, fillcolor=_DOWN, opacity=0.12, line_width=0)
        fig.add_trace(go.Scatter(x=x, y=data["primary"], mode="lines", name=data["primary_name"],
                                  line=dict(color=_UP, width=2)))
        fig.update_layout(**_PATTERN_LAYOUT)
        fig.update_yaxes(range=[0, 100])
        return fig

    if kind == "band":
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=data["band_upper"], mode="lines", line=dict(width=0),
                                  showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=x, y=data["band_lower"], mode="lines", line=dict(width=0),
                                  fill="tonexty", fillcolor="rgba(78,154,121,0.15)",
                                  name=data["band_name"], hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=x, y=data["primary"], mode="lines", name=data["primary_name"],
                                  line=dict(color=_INK, width=2)))
        fig.update_layout(**_PATTERN_LAYOUT)
        return fig

    if kind == "adx":
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=data["adx"], mode="lines", name="ADX",
                                  line=dict(color=_INK, width=2)))
        fig.add_trace(go.Scatter(x=x, y=data["plus_di"], mode="lines", name="+DI",
                                  line=dict(color=_UP, width=1.5, dash="dot")))
        fig.add_trace(go.Scatter(x=x, y=data["minus_di"], mode="lines", name="-DI",
                                  line=dict(color=_DOWN, width=1.5, dash="dot")))
        fig.add_hline(y=25, line=dict(color=_HAIRLINE_STRONG, width=1, dash="dash"))
        fig.update_layout(**_PATTERN_LAYOUT)
        return fig

    raise ValueError(f"unknown pattern chart kind: {kind}")


def build_pattern_candlestick_chart(df: pd.DataFrame) -> go.Figure:
    """チャート学習ページ用の、ローソク足パターンの見た目を伝えるための簡易ローソク足図。"""
    fig = go.Figure(go.Candlestick(
        x=df.index, open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing_line_color=_UP, decreasing_line_color=_DOWN,
        increasing_fillcolor=_UP, decreasing_fillcolor=_DOWN,
    ))
    fig.update_layout(
        margin=dict(l=8, r=8, t=8, b=8),
        height=180,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, fixedrange=True, rangeslider=dict(visible=False)),
        yaxis=dict(visible=False, fixedrange=True),
    )
    return fig


def build_price_chart(df: pd.DataFrame, ticker: str, show_ma: list, ja: bool = True) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.75, 0.25]
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name=ticker,
            increasing_line_color=_UP,
            decreasing_line_color=_DOWN,
        ),
        row=1, col=1,
    )

    ma_styles = {
        "MA20": (_CLAY, "MA20"),
        "MA50": (_STONE, "MA50"),
        "MA200": (_MAUVE, "MA200"),
    }
    for key, (color, label) in ma_styles.items():
        if key in show_ma:
            col = key.lower()
            fig.add_trace(
                go.Scatter(x=df.index, y=df[col], name=label,
                           line=dict(color=color, width=1.5)),
                row=1, col=1,
            )

    if "BB" in show_ma:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["bb_upper"], name="BB上限" if ja else "BB Upper",
                       line=dict(color="rgba(166,163,153,0.55)", width=1, dash="dash")),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df["bb_lower"], name="BB下限" if ja else "BB Lower",
                       line=dict(color="rgba(166,163,153,0.55)", width=1, dash="dash"),
                       fill="tonexty", fillcolor="rgba(166,163,153,0.08)"),
            row=1, col=1,
        )

    if "VWAP" in show_ma:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["vwap"], name="VWAP(20)",
                       line=dict(color=_GOLD, width=1.5, dash="dot")),
            row=1, col=1,
        )

    if "一目雲" in show_ma:
        _add_ichimoku_traces(fig, df, ja)

    vol_colors = [
        _UP if c >= o else _DOWN
        for c, o in zip(df["close"], df["open"])
    ]
    fig.add_trace(
        go.Bar(x=df.index, y=df["volume"], name="出来高" if ja else "Volume",
               marker_color=vol_colors, opacity=0.6),
        row=2, col=1,
    )

    fig.update_layout(
        title=f"{ticker} 価格チャート" if ja else f"{ticker} Price Chart",
        xaxis_rangeslider_visible=False,
        height=580,
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=20),
        **_TRANSPARENT_LAYOUT,
    )
    fig.update_yaxes(title_text="価格" if ja else "Price", row=1, col=1)
    fig.update_yaxes(title_text="出来高" if ja else "Volume", row=2, col=1)

    return fig


def build_rsi_chart(df: pd.DataFrame, ja: bool = True) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index, y=df["rsi"],
        name="RSI(14)",
        line=dict(color=_GOLD, width=2),
    ))

    fig.add_hrect(y0=70, y1=100, fillcolor=_DOWN, opacity=0.08, line_width=0)
    fig.add_hrect(y0=0, y1=30, fillcolor=_UP, opacity=0.08, line_width=0)
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(192,91,63,0.6)",
                  annotation_text="売られすぎ 70" if ja else "Overbought 70",
                  annotation_position="right")
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(78,154,121,0.6)",
                  annotation_text="買われすぎ 30" if ja else "Oversold 30",
                  annotation_position="right")
    fig.add_hline(y=50, line_dash="dot", line_color="rgba(166,163,153,0.4)")

    fig.update_layout(
        title="RSI（相対力指数）" if ja else "RSI (Relative Strength Index)",
        height=220,
        template="plotly_dark",
        yaxis=dict(range=[0, 100]),
        margin=dict(t=40, b=20),
        showlegend=False,
        **_TRANSPARENT_LAYOUT,
    )
    return fig


def build_macd_chart(df: pd.DataFrame, ja: bool = True) -> go.Figure:
    hist_colors = [
        _UP if v >= 0 else _DOWN
        for v in df["macd_hist"].fillna(0)
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df.index, y=df["macd_hist"],
        name="ヒストグラム" if ja else "Histogram",
        marker_color=hist_colors,
        opacity=0.7,
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["macd"],
        name="MACD",
        line=dict(color=_STONE, width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["macd_signal"],
        name="シグナル" if ja else "Signal",
        line=dict(color=_GOLD, width=1.5),
    ))

    fig.add_hline(y=0, line_dash="dash", line_color="rgba(166,163,153,0.4)")

    fig.update_layout(
        title="MACD",
        height=220,
        template="plotly_dark",
        margin=dict(t=40, b=20),
        legend=dict(orientation="h"),
        **_TRANSPARENT_LAYOUT,
    )
    return fig


def build_adx_chart(df: pd.DataFrame, ja: bool = True) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index, y=df["adx"], name="ADX",
        line=dict(color=_INK, width=2),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["plus_di"], name="+DI",
        line=dict(color=_UP, width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["minus_di"], name="-DI",
        line=dict(color=_DOWN, width=1.5),
    ))

    fig.add_hline(y=25, line_dash="dash", line_color="rgba(166,163,153,0.5)",
                  annotation_text="トレンドあり 25" if ja else "Trending 25",
                  annotation_position="right")

    fig.update_layout(
        title="ADX（トレンド強度）/ +DI・-DI" if ja else "ADX (Trend Strength) / +DI/-DI",
        height=220,
        template="plotly_dark",
        margin=dict(t=40, b=20),
        legend=dict(orientation="h"),
        **_TRANSPARENT_LAYOUT,
    )
    return fig


def build_obv_chart(df: pd.DataFrame, ja: bool = True) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index, y=df["obv"], name="OBV",
        line=dict(color=_GOLD, width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["obv_ema"], name="OBV EMA20",
        line=dict(color=_STONE, width=1.5, dash="dot"),
    ))

    fig.update_layout(
        title="OBV（出来高バランス）" if ja else "OBV (On-Balance Volume)",
        height=220,
        template="plotly_dark",
        margin=dict(t=40, b=20),
        legend=dict(orientation="h"),
        **_TRANSPARENT_LAYOUT,
    )
    return fig


def build_comparison_chart(
    df: pd.DataFrame,
    idx_df: pd.DataFrame,
    ticker: str,
    idx_name: str,
    ja: bool = True,
) -> go.Figure:
    # 共通期間に揃える
    start = max(df.index[0], idx_df.index[0])
    df_trim = df[df.index >= start]
    idx_trim = idx_df[idx_df.index >= start]

    if df_trim.empty or idx_trim.empty:
        return go.Figure()

    stock_norm = df_trim["close"] / df_trim["close"].iloc[0] * 100
    idx_norm = idx_trim["close"] / idx_trim["close"].iloc[0] * 100

    stock_ret = stock_norm.iloc[-1] - 100
    idx_ret = idx_norm.iloc[-1] - 100
    alpha = stock_ret - idx_ret

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_trim.index, y=stock_norm,
        name=f"{ticker} ({stock_ret:+.1f}%)",
        line=dict(color=_GOLD, width=2),
    ))
    fig.add_trace(go.Scatter(
        x=idx_trim.index, y=idx_norm,
        name=f"{idx_name} ({idx_ret:+.1f}%)",
        line=dict(color=_STONE, width=2),
    ))
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(166,163,153,0.4)")

    sign = "+" if alpha >= 0 else ""
    title = (
        f"相対パフォーマンス比較（期初=100）　超過リターン: {sign}{alpha:.1f}%" if ja
        else f"Relative Performance (Start=100)   Alpha: {sign}{alpha:.1f}%"
    )
    fig.update_layout(
        title=title,
        height=320,
        template="plotly_dark",
        yaxis_title="相対パフォーマンス" if ja else "Relative Performance",
        margin=dict(t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **_TRANSPARENT_LAYOUT,
    )
    return fig
