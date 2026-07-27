from http import HTTPStatus
from typing import final

from django.utils.translation import gettext_lazy as _

from services.api.common.exceptions import BaseAPIError


@final
class CompanyNotFoundError(BaseAPIError):
    """Report a request for a company that does not exist."""

    message = _("Company not found.")
    status_code = HTTPStatus.NOT_FOUND
