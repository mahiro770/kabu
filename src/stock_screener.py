import queue
import threading

import ollama
from typing import Generator


def build_screening_prompt(news_items: list[dict]) -> str:
    lines = [f"{i}. [{item.get('source', '')}] {item['title']}"
             for i, item in enumerate(news_items, 1)]
    news_block = "\n".join(lines)

    return f"""あなたは10年以上の経験を持つプロの株式アナリストです。以下は本日までに配信された経済・市況ニュースの見出し一覧です。これらの見出しから、翌営業日以降に株価が動く可能性が高い銘柄を抽出し、注目度順にランキングしてください。

## ニュース見出し一覧
{news_block}

---

以下の形式で日本語のレポートを作成してください：

### 注目銘柄ランキング
表形式で、順位・銘柄名・ティッカー（わかる範囲で。日本株は証券コード+.T、米国株はティッカーシンボル）・関連ニュース（該当する見出し番号）・注目理由・想定インパクト（ポジティブ/ネガティブ/中立）をまとめてください（最大10銘柄）。見出しから銘柄が直接特定できない場合は無理に挙げず、関連が明確なものだけを選んでください。

### 全体の相場観
本日のニュース全体から読み取れる市場全体の地合いや、注意すべきセクター・テーマを2〜3文で述べてください。

### 注意事項
この分析はニュース見出しのみに基づく速報的な参考情報であり、投資判断の根拠とするものではありません。投資は自己責任でお願いします。
"""


def screen_stocks_stream(news_items: list[dict], model: str) -> Generator[str, None, None]:
    if not news_items:
        yield "分析対象のニュースを取得できませんでした。"
        return

    prompt = build_screening_prompt(news_items)
    try:
        stream = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield content
    except Exception as e:
        yield f"\n\n**エラーが発生しました**\n\n```\n{e}\n```\n\nOllamaが起動していることを確認してください: `ollama serve`"


def screen_stocks_stream_with_timeout(
    news_items: list[dict],
    model: str,
    timeout: float = 90,
) -> Generator[str, None, None]:
    """screen_stocks_streamをラップし、chunk間が`timeout`秒空いたら諦めてタイムアウトメッセージを返す。

    モデルの応答自体はバックグラウンドスレッドで継続する可能性があるが、
    呼び出し側（UI）はブロックされずに次のモデルへ進める。
    """
    q: queue.Queue = queue.Queue()
    _DONE = object()

    def worker():
        try:
            for chunk in screen_stocks_stream(news_items, model):
                q.put(chunk)
        except Exception as e:
            q.put(f"\n\n**エラーが発生しました**\n\n```\n{e}\n```")
        finally:
            q.put(_DONE)

    threading.Thread(target=worker, daemon=True).start()

    while True:
        try:
            item = q.get(timeout=timeout)
        except queue.Empty:
            yield (
                f"\n\n**タイムアウトしました（{timeout:.0f}秒応答なし）**\n\n"
                f"`{model}` からの応答がありませんでした。モデルの読み込みに時間がかかっているか、"
                "処理待ちが混雑している可能性があります。時間をおくか、別のモデルをお試しください。"
            )
            return
        if item is _DONE:
            return
        yield item
