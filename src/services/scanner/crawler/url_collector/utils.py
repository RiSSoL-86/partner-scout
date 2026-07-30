from urllib.parse import urlparse


def is_in_scope(url: str, domain: str) -> bool:
    """Tell whether a URL stays on the given company domain."""
    netloc = urlparse(url).netloc.removeprefix("www.")
    return netloc == domain.removeprefix("www.")
