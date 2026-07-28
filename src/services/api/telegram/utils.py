from http import HTTPStatus
from math import ceil
from typing import Any

from asgiref.sync import sync_to_async
from django.http import HttpResponse
from django.template.loader import render_to_string


def paginate(page: int, page_size: int, total: int) -> dict[str, int | bool]:
    """Return pagination metadata for a page of ``total`` items."""
    total_pages = max(1, ceil(total / page_size)) if page_size else 1
    has_prev = page > 1
    has_next = page < total_pages
    return {
        "page": page,
        "total_pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next,
        "prev_page": page - 1 if has_prev else page,
        "next_page": page + 1 if has_next else page,
    }


async def render_html(
    status: HTTPStatus,
    context: dict[str, Any],
    template_name: str,
) -> HttpResponse:
    """Render a template to an HTML ``HttpResponse`` off the event loop."""
    html = await sync_to_async(
        func=render_to_string,
        thread_sensitive=False,
    )(template_name, context=context)
    return HttpResponse(
        html,
        status=status,
        content_type="text/html; charset=utf-8",
    )
