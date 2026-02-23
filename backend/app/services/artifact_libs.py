"""Helper for loading vendored JS libraries for artifact rendering in headless browser.

In airgapped deployments, CDN URLs are not available. This module reads the
vendored JS files from disk and returns them as inline <script> tags for use
with Playwright's page.set_content() (which renders at about:blank and cannot
resolve relative paths).
"""

import logging
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

# Paths where vendored libs may be found (checked in order):
# 1. Nuxt build output (production Docker image)
# 2. Frontend public dir (local development / Docker with public copied)
_CANDIDATE_DIRS = [
    Path(__file__).parent.parent.parent.parent / "frontend" / ".output" / "public" / "libs",
    Path(__file__).parent.parent.parent.parent / "frontend" / "public" / "libs",
]

# Libraries needed for dashboard (page) mode artifacts
_PAGE_LIBS = [
    "tailwindcss-3.4.16.js",
    "react-18.production.min.js",
    "react-dom-18.production.min.js",
    "babel-standalone.min.js",
    "echarts-5.min.js",
]

# Libraries needed for slides mode artifacts
_SLIDES_LIBS = [
    "tailwindcss-3.4.16.js",
]


def _find_libs_dir() -> Path | None:
    """Find the directory containing vendored JS libraries."""
    for d in _CANDIDATE_DIRS:
        if d.is_dir() and any(d.iterdir()):
            return d
    return None


@lru_cache(maxsize=1)
def _read_lib(libs_dir: Path, filename: str) -> str:
    """Read a vendored JS file and return its contents."""
    path = libs_dir / filename
    return path.read_text(encoding="utf-8")


def get_inline_scripts(mode: str = "page") -> str:
    """Return inline <script> tags with vendored JS library contents.

    Args:
        mode: 'page' for React/Babel/ECharts dashboard, 'slides' for Tailwind-only.

    Returns:
        HTML string with <script>...</script> tags containing the library code.
        Returns CDN fallback tags if vendored files are not found.
    """
    libs_dir = _find_libs_dir()

    if libs_dir is None:
        logger.warning("Vendored JS libs not found, falling back to CDN URLs")
        return _cdn_fallback_tags(mode)

    lib_files = _PAGE_LIBS if mode == "page" else _SLIDES_LIBS
    parts = []

    for filename in lib_files:
        try:
            content = _read_lib(libs_dir, filename)
            parts.append(f"<script>{content}</script>")
        except FileNotFoundError:
            logger.warning(f"Vendored lib not found: {filename}, using CDN fallback")
            parts.append(_cdn_fallback_for(filename))

    return "\n".join(parts)


def _cdn_fallback_tags(mode: str) -> str:
    """Return CDN script tags as fallback when vendored files are unavailable."""
    if mode == "slides":
        return '<script src="https://cdn.tailwindcss.com"></script>'

    return """<script src="https://cdn.tailwindcss.com"></script>
<script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>"""


def _cdn_fallback_for(filename: str) -> str:
    """Return a single CDN fallback tag for a specific library file."""
    mapping = {
        "tailwindcss-3.4.16.js": '<script src="https://cdn.tailwindcss.com"></script>',
        "react-18.production.min.js": '<script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>',
        "react-dom-18.production.min.js": '<script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>',
        "babel-standalone.min.js": '<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>',
        "echarts-5.min.js": '<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>',
    }
    return mapping.get(filename, "")
