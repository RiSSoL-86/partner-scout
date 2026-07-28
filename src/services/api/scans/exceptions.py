from http import HTTPStatus
from typing import final

from django.utils.translation import gettext_lazy as _

from services.api.common.exceptions import BaseAPIError


@final
class ScanNotFoundError(BaseAPIError):
    """Report a request for a scan that does not exist."""

    message = _("Scan not found.")
    status_code = HTTPStatus.NOT_FOUND


@final
class PersonNotInScanError(BaseAPIError):
    """Report a request for a person absent from the given scan."""

    message = _("Person not found in this scan.")
    status_code = HTTPStatus.NOT_FOUND
