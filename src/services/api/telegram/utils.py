from http import HTTPStatus
from typing import Any

from asgiref.sync import sync_to_async
from django.http import HttpResponse
from django.template.loader import render_to_string


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
