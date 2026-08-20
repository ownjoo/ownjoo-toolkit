"""Extract readable content from HTML -- the login-page-instead-of-JSON case.

APIs sometimes respond to a request with an HTML page instead of the expected payload:
a proxy's auth challenge, a load balancer's error page, a captive portal. The response
still has a 200 (or a stray 3xx/4xx) and a body, but it's markup, not data. strip_html()
pulls out what's actually informative -- the page title, then the visible text -- and
drops everything that isn't (script, style, head metadata, SVG icons, <template>
contents).

BeautifulSoup is an optional dependency: importing oj_toolkit.parsing.html never
requires it, only calling strip_html() does (via a lazy import). Install it with:
pip install 'oj-toolkit[html]'
"""

from typing import Iterable

_BS4_INSTALL_HINT = "beautifulsoup4 is not installed. Install it with: pip install 'oj-toolkit[html]'"

DEFAULT_DROP_TAGS: tuple[str, ...] = (
    "script",
    "style",
    "head",
    "meta",
    "link",
    "noscript",
    "svg",
    "template",
)


def strip_html(html: str, drop_tags: Iterable[str] = DEFAULT_DROP_TAGS) -> str:
    """Strip non-content tags from an HTML document and return the remaining text.

    The <title> (if any) is captured before drop_tags are applied -- even though it
    normally lives inside <head> -- and prepended as the first line, since it's often
    the single most informative thing on an unexpected HTML response
    ("Sign In - Acme SSO").

    Args:
        html: Raw HTML, e.g. an HTTP response body.
        drop_tags: Tag names removed (along with their contents) before text
            extraction. Default: script, style, head, meta, link, noscript, svg,
            template.

    Returns:
        The title (if present and non-empty) followed by visible text, one line per
        text node, blank lines collapsed. Empty string if nothing remains.

    Example:
        >>> strip_html('<html><head><title>Sign In</title></head><body>'
        ...             '<script>track()</script><h1>Session expired</h1></body></html>')
        'Sign In\\nSession expired'
    """
    try:
        from bs4 import BeautifulSoup  # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        raise ImportError(_BS4_INSTALL_HINT) from exc

    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    for tag in soup(list(drop_tags)):
        tag.decompose()

    lines = [line.strip() for line in soup.get_text(separator="\n").splitlines()]
    body_text = "\n".join(line for line in lines if line)

    return "\n".join(line for line in (title, body_text) if line)
