from urllib.parse import urlparse

from django.conf import settings


def strip_language_prefix(path: str) -> str:
    """Remove /uz/, /ru/, /en/ prefix from path."""
    if not path:
        return "/"

    parsed = urlparse(path)
    clean = parsed.path or "/"

    for code, _ in settings.LANGUAGES:
        if clean == f"/{code}":
            clean = "/"
            break
        prefix = f"/{code}/"
        if clean.startswith(prefix):
            clean = "/" + clean[len(prefix) :]
            break

    return clean


def localize_path(path: str, lang_code: str) -> str:
    """
    Build the same page URL for a target language.

    Works correctly with prefix_default_language=False where default lang (uz)
    has no URL prefix but ru/en do.
    """
    parsed = urlparse(path)
    clean = strip_language_prefix(path)
    default = settings.LANGUAGE_CODE
    prefix_default = getattr(settings, "prefix_default_language", False)

    if lang_code == default and not prefix_default:
        localized = clean
    elif clean == "/":
        localized = f"/{lang_code}/"
    else:
        localized = f"/{lang_code}{clean}"

    if parsed.query:
        localized = f"{localized}?{parsed.query}"

    return localized or "/"
