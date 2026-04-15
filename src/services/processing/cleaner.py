"""Text cleaning utilities for HTML documents."""

from bs4 import BeautifulSoup


def clean_html(html: str) -> str:
    """Strip boilerplate tags and normalize extracted text."""

    soup = BeautifulSoup(html, "html.parser")
    for tag_name in (
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "noscript",
        "form",
        "aside",
        "svg",
    ):
        for node in soup.find_all(tag_name):
            node.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())
