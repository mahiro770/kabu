import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def _add_ichimoku_traces(fig: go.Figure, df: pd.DataFrame) -> None:
    fig.add_trace(
        go.Scatter(x=df.index, y=df["ichimoku_tenkan"], name="転換線",
                   line=dict(color="#ef5350", width=1)),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["ichimoku_kijun"], name="基準線",
                   line=dict(color="#1f77b4", width=1)),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["ichimoku_chikou"], name="遅行スパン",
                   line=dict(color="#9b59b6", width=1, dash="dot")),
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
        go.Scatter(x=cloud_index, y=senkou_b, name="先行スパンB",
                   line=dict(color="rgba(239,83,80,0.4)", width=1)),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=cloud_index, y=senkou_a, name="先行スパンA（雲）",
                   line=dict(color="rgba(38,166,154,0.4)", width=1),
                   fill="tonexty", fillcolor="rgba(120,140,160,0.15)"),
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
            tickfont=dict(size=10, color="#9ca3af"), fixedrange=True,
        ),
        yaxis=dict(
            side="right", showgrid=True, gridcolor="rgba(255,255,255,0.08)", griddash="dash",
            tickfont=dict(size=10, color="#9ca3af"), fixedrange=True,
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
            tickfont=dict(size=9, color="#9ca3af"), fixedrange=True,
        ),
        yaxis=dict(
            visible=True, side="right", showgrid=True, gridcolor="rgba(255,255,255,0.08)",
            griddash="dash", nticks=3, tickfont=dict(size=9, color="#9ca3af"), fixedrange=True,
        ),
    )
    return fig


def build_price_chart(df: pd.DataFrame, ticker: str, show_ma: list) -> go.Figure:
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
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
        ),
        row=1, col=1,
    )

    ma_styles = {
        "MA20": ("#1f77b4", "MA20"),
        "MA50": ("#ff7f0e", "MA50"),
        "MA200": ("#2ca02c", "MA200"),
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
            go.Scatter(x=df.index, y=df["bb_upper"], name="BB上限",
                       line=dict(color="rgba(180,180,180,0.6)", width=1, dash="dash")),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df["bb_lower"], name="BB下限",
                       line=dict(color="rgba(180,180,180,0.6)", width=1, dash="dash"),
                       fill="tonexty", fillcolor="rgba(150,150,150,0.08)"),
            row=1, col=1,
        )

    if "VWAP" in show_ma:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["vwap"], name="VWAP(20)",
                       line=dict(color="#e91e8c", width=1.5, dash="dot")),
            row=1, col=1,
        )

    if "一目雲" in show_ma:
        _add_ichimoku_traces(fig, df)

    vol_colors = [
        "#26a69a" if c >= o else "#ef5350"
        for c, o in zip(df["close"], df["open"])
    ]
    fig.add_trace(
        go.Bar(x=df.index, y=df["volume"], name="出来高",
               marker_color=vol_colors, opacity=0.6),
        row=2, col=1,
    )

    fig.update_layout(
        title=f"{ticker} 価格チャート",
        xaxis_rangeslider_visible=False,
        height=580,
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=20),
    )
    fig.update_yaxes(title_text="価格", row=1, col=1)
    fig.update_yaxes(title_text="出来高", row=2, col=1)

    return fig


def build_rsi_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index, y=df["rsi"],
        name="RSI(14)",
        line=dict(color="#9b59b6", width=2),
    ))

    fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.05, line_width=0)
    fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.05, line_width=0)
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(255,80,80,0.6)",
                  annotation_text="売られすぎ 70", annotation_position="right")
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(80,200,80,0.6)",
                  annotation_text="買われすぎ 30", annotation_position="right")
    fig.add_hline(y=50, line_dash="dot", line_color="rgba(150,150,150,0.4)")

    fig.update_layout(
        title="RSI（相対力指数）",
        height=220,
        template="plotly_dark",
        yaxis=dict(range=[0, 100]),
        margin=dict(t=40, b=20),
        showlegend=False,
    )
    return fig


def build_macd_chart(df: pd.DataFrame) -> go.Figure:
    hist_colors = [
        "#26a69a" if v >= 0 else "#ef5350"
        for v in df["macd_hist"].fillna(0)
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df.index, y=df["macd_hist"],
        name="ヒストグラム",
        marker_color=hist_colors,
        opacity=0.7,
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["macd"],
        name="MACD",
        line=dict(color="#1f77b4", width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["macd_signal"],
        name="シグナル",
        line=dict(color="#ff7f0e", width=1.5),
    ))

    fig.add_hline(y=0, line_dash="dash", line_color="rgba(150,150,150,0.4)")

    fig.update_layout(
        title="MACD",
        height=220,
        template="plotly_dark",
        margin=dict(t=40, b=20),
        legend=dict(orientation="h"),
    )
    return fig


def build_adx_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index, y=df["adx"], name="ADX",
        line=dict(color="#f3f4f6", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["plus_di"], name="+DI",
        line=dict(color="#26a69a", width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["minus_di"], name="-DI",
        line=dict(color="#ef5350", width=1.5),
    ))

    fig.add_hline(y=25, line_dash="dash", line_color="rgba(150,150,150,0.5)",
                  annotation_text="トレンドあり 25", annotation_position="right")

    fig.update_layout(
        title="ADX（トレンド強度）/ +DI・-DI",
        height=220,
        template="plotly_dark",
        margin=dict(t=40, b=20),
        legend=dict(orientation="h"),
    )
    return fig


def build_obv_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index, y=df["obv"], name="OBV",
        line=dict(color="#8b5cf6", width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["obv_ema"], name="OBV EMA20",
        line=dict(color="#22d3ee", width=1.5, dash="dot"),
    ))

    fig.update_layout(
        title="OBV（出来高バランス）",
        height=220,
        template="plotly_dark",
        margin=dict(t=40, b=20),
        legend=dict(orientation="h"),
    )
    return fig


def build_comparison_chart(
    df: pd.DataFrame,
    idx_df: pd.DataFrame,
    ticker: str,
    idx_name: str,
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
        line=dict(color="#1f77b4", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=idx_trim.index, y=idx_norm,
        name=f"{idx_name} ({idx_ret:+.1f}%)",
        line=dict(color="#ff7f0e", width=2),
    ))
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(180,180,180,0.4)")

    sign = "+" if alpha >= 0 else ""
    fig.update_layout(
        title=f"相対パフォーマンス比較（期初=100）　超過リターン: {sign}{alpha:.1f}%",
        height=320,
        template="plotly_dark",
        yaxis_title="相対パフォーマンス",
        margin=dict(t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig
