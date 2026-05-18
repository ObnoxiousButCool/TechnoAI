"""Text cleaning utilities for HTML documents."""

from __future__ import annotations

from bs4 import BeautifulSoup

STRIP_TAGS = (
    "script", "style", "nav", "footer", "header",
    "noscript", "form", "aside", "svg", "iframe",
    "button", "input", "select", "textarea",
)


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag_name in STRIP_TAGS:
        for node in soup.find_all(tag_name):
            node.decompose()

    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find(id="content")
        or soup.find(id="main")
        or soup
    )

    segments = []
    for node in main.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th", "blockquote"]):
        text = node.get_text(separator=" ", strip=True)
        if text and len(text) > 8:
            segments.append(text)

    seen = set()
    deduped = []
    for s in segments:
        if s not in seen:
            seen.add(s)
            deduped.append(s)

    if not deduped:
        text = main.get_text(separator=" ", strip=True)
        return " ".join(text.split())

    return " | ".join(deduped)
