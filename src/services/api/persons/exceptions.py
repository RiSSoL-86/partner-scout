from http import HTTPStatus
from typing import final

from django.utils.translation import gettext_lazy as _

from services.api.common.exceptions import BaseAPIError


@final
class PersonNotFoundError(BaseAPIError):
    """Report a request for a person that does not exist."""

    message = _("Person not found.")
    status_code = HTTPStatus.NOT_FOUND
