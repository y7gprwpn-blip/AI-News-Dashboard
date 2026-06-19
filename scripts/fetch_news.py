#!/usr/bin/env python3
import json
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

import feedparser


NEWS_PATH = Path("news.json")

FEEDS = [
    {"url": "https://techcrunch.com/feed/", "source": "TechCrunch"},
    {"url": "https://www.technologyreview.com/feed/", "source": "MIT Technology Review"},
    {"url": "https://www.nature.com/subjects/artificial-intelligence/rss", "source": "Nature AI"},
    {"url": "https://www.scmp.com/rss/technology/topics/china-ai", "source": "SCMP China AI"},
    {"url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "source": "The Verge AI"},
    {
        "url": "https://news.google.com/rss/search?q=AI&hl=ja&gl=JP&ceid=JP:ja",
        "source": "Google News: AI",
    },
    {
        "url": "https://news.google.com/rss/search?q=%E7%94%9F%E6%88%90AI&hl=ja&gl=JP&ceid=JP:ja",
        "source": "Google News: 生成AI",
    },
    {
        "url": "https://news.google.com/rss/search?q=%E5%8C%BB%E7%99%82AI&hl=ja&gl=JP&ceid=JP:ja",
        "source": "Google News: 医療AI",
    },
    {
        "url": "https://news.google.com/rss/search?q=%E7%94%BB%E5%83%8F%E7%94%9F%E6%88%90AI&hl=ja&gl=JP&ceid=JP:ja",
        "source": "Google News: 画像生成AI",
    },
    {
        "url": "https://news.google.com/rss/search?q=AI%20%E8%91%97%E4%BD%9C%E6%A8%A9&hl=ja&gl=JP&ceid=JP:ja",
        "source": "Google News: AI 著作権",
    },
    {
        "url": "https://news.google.com/rss/search?q=%E4%B8%AD%E5%9B%BD%20AI&hl=ja&gl=JP&ceid=JP:ja",
        "source": "Google News: 中国 AI",
    },
    {"url": "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml", "source": "ITmedia NEWS"},
    {"url": "https://pc.watch.impress.co.jp/data/rss/1.0/pcw/feed.rdf", "source": "PC Watch"},
    {"url": "https://internet.watch.impress.co.jp/data/rss/1.0/iw/feed.rdf", "source": "INTERNET Watch"},
    {"url": "https://gigazine.net/news/rss_2.0/", "source": "GIGAZINE"},
]

CATEGORIES = [
    (
        "医療ライター",
        [
            "medical writer",
            "medical writing",
            "health writer",
            "patient education",
            "pharma content",
            "medical content",
            "医療ライター",
            "医療記事",
            "患者向け",
            "監修",
        ],
    ),
    (
        "医療イラスト",
        [
            "medical illustration",
            "medical illustrator",
            "anatomy illustration",
            "patient illustration",
            "clinical illustration",
            "医療イラスト",
            "解剖図",
            "患者説明",
        ],
    ),
    (
        "医療AI",
        [
            "medical ai",
            "healthcare ai",
            "clinical ai",
            "diagnosis",
            "radiology",
            "drug discovery",
            "hospital",
            "医療ai",
            "医療",
            "診断",
            "読影",
            "創薬",
            "病院",
            "ヘルスケア",
        ],
    ),
    (
        "動画生成AI",
        [
            "video generation",
            "generative video",
            "text-to-video",
            "sora",
            "runway",
            "pika",
            "動画生成",
            "ai動画",
            "映像生成",
        ],
    ),
    (
        "画像生成AI",
        [
            "image generation",
            "generative image",
            "text-to-image",
            "dall-e",
            "midjourney",
            "stable diffusion",
            "flux",
            "画像生成",
            "ai画像",
            "イラスト生成",
        ],
    ),
    (
        "中国AI",
        [
            "china",
            "chinese ai",
            "baidu",
            "tencent",
            "alibaba",
            "deepseek",
            "bytedance",
            "中国ai",
            "中国",
            "百度",
            "テンセント",
            "アリババ",
        ],
    ),
    (
        "AI規制・著作権",
        [
            "regulation",
            "policy",
            "copyright",
            "intellectual property",
            "lawsuit",
            "licensing",
            "ai act",
            "規制",
            "著作権",
            "知的財産",
            "訴訟",
            "ガイドライン",
            "文化庁",
        ],
    ),
    (
        "AI全般",
        [
            "generative ai",
            "artificial intelligence",
            "chatgpt",
            "openai",
            "claude",
            "gemini",
            "llm",
            "ai agent",
            "生成ai",
            "人工知能",
            "大規模言語モデル",
            "ai",
        ],
    ),
]

CATEGORY_IMPORTANCE = {
    "AI全般": "AIの使われ方や競争環境が変わる可能性があります。",
    "医療AI": "医療現場での安全性、精度、運用体制に関わる動きです。",
    "医療ライター": "医療情報の作成、監修、読者への伝え方に影響します。",
    "医療イラスト": "患者説明や教材制作で、正確性と表現力の両立が問われます。",
    "画像生成AI": "制作現場の効率化と、権利・品質管理の両方に関わります。",
    "動画生成AI": "広告、教育、SNS向け動画制作のワークフローに影響します。",
    "中国AI": "中国企業や政策の動きは、価格競争や技術潮流を見る材料になります。",
    "AI規制・著作権": "AI利用ルールやクリエイター保護の実務に関わる論点です。",
}

CATEGORY_VIEWPOINTS = {
    "AI全般": "まどかAI観測所では、どの仕事や生活シーンに広がるかを見ます。",
    "医療AI": "まどかAI観測所では、臨床で本当に使える形になるかを見ます。",
    "医療ライター": "まどかAI観測所では、AI下書きと人間の監修の分担を見ます。",
    "医療イラスト": "まどかAI観測所では、医学的な正確性をどう守るかを見ます。",
    "画像生成AI": "まどかAI観測所では、制作工程と著作権対応の変化を見ます。",
    "動画生成AI": "まどかAI観測所では、動画制作のコストと信頼性の変化を見ます。",
    "中国AI": "まどかAI観測所では、日本や海外市場への影響を見ます。",
    "AI規制・著作権": "まどかAI観測所では、実務で何を変える必要があるかを見ます。",
}

MAX_ITEMS_PER_CATEGORY = 8
HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[。.!?！？])\s*")


def normalize_text(value):
    if not value:
        return ""
    text = unescape(str(value)).replace("\xa0", " ")
    text = HTML_TAG_RE.sub("", text)
    return WHITESPACE_RE.sub(" ", text).strip()


def parse_date(entry):
    if getattr(entry, "published_parsed", None):
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    if getattr(entry, "updated_parsed", None):
        return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def classify(entry_text):
    text = entry_text.lower()
    for category, keywords in CATEGORIES:
        if any(keyword.lower() in text for keyword in keywords):
            return category
    if "ai" in text or "人工知能" in text:
        return "AI全般"
    return None


def trim_text(text, max_length=86):
    text = normalize_text(text)
    if len(text) <= max_length:
        return text
    return text[: max_length - 1].rstrip() + "…"


def make_memo(summary):
    if not summary:
        return "詳細はリンク先で確認してください。"
    return trim_text(summary, 80)


def pick_lead_sentence(title, summary):
    for sentence in SENTENCE_SPLIT_RE.split(summary):
        sentence = normalize_text(sentence)
        if sentence:
            return trim_text(sentence, 92)
    return trim_text(f"{title}について報じられています。", 92)


def make_summary_lines(title, summary, category):
    lead = pick_lead_sentence(title, summary)
    return [
        lead,
        CATEGORY_IMPORTANCE.get(category, "AIの利用や社会実装に関わる動きです。"),
        CATEGORY_VIEWPOINTS.get(category, "まどかAI観測所では、今後の影響と実用性を見ます。"),
    ]


def load_entries():
    entries = []
    failed_feeds = []
    seen_links = set()
    for feed in FEEDS:
        parsed = feedparser.parse(feed["url"])
        if getattr(parsed, "bozo", False) and not parsed.entries:
            error = str(parsed.bozo_exception)
            print(f"skip feed: {feed['source']} ({error})")
            failed_feeds.append(
                {
                    "source": feed["source"],
                    "url": feed["url"],
                    "error": error,
                }
            )
            continue

        for entry in parsed.entries:
            title = normalize_text(getattr(entry, "title", ""))
            summary = normalize_text(getattr(entry, "summary", getattr(entry, "description", "")))
            link = getattr(entry, "link", "")
            if not link or link in seen_links:
                continue

            pub_date = parse_date(entry)
            category = classify(" ".join([title, summary, feed["source"]]))
            if not category or not title:
                continue

            seen_links.add(link)
            entries.append(
                {
                    "title": title,
                    "memo": make_memo(summary),
                    "summaryLines": make_summary_lines(title, summary, category),
                    "link": link,
                    "source": feed["source"],
                    "pub_date": pub_date,
                    "category": category,
                }
            )
    return entries, failed_feeds


def build_news(items, failed_feeds):
    items_sorted = sorted(items, key=lambda item: item["pub_date"], reverse=True)
    selected = []
    category_counts = {category: 0 for category, _ in CATEGORIES}

    for item in items_sorted:
        if category_counts[item["category"]] >= MAX_ITEMS_PER_CATEGORY:
            continue
        category_counts[item["category"]] += 1
        selected.append(
            {
                "title": item["title"],
                "link": item["link"],
                "pubDate": item["pub_date"].astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                "source": item["source"],
                "category": item["category"],
                "memo": item["memo"],
                "summaryLines": item["summaryLines"],
            }
        )

    return {
        "updated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "items": selected,
        "errors": failed_feeds,
    }


def main():
    entries, failed_feeds = load_entries()
    news = build_news(entries, failed_feeds)
    with NEWS_PATH.open("w", encoding="utf-8") as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {len(news['items'])} items to {NEWS_PATH}.")
    if not news["items"]:
        print("RSS取得結果がありません。")


if __name__ == "__main__":
    main()
