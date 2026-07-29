import logging
from typing import final, override
from uuid import UUID

from django.db import IntegrityError

from apps.common.services.base import BaseService
from apps.companies.repository import CompanyRepository
from apps.scans.choices import ScanStatus
from apps.scans.models import Scan
from apps.scans.repository import ScanRepository

logger = logging.getLogger(__name__)


@final
class ScanPlanService(BaseService):
    """Open a pending scan for every scan-enabled company."""

    company_repository = CompanyRepository()
    scan_repository = ScanRepository()

    @override
    async def execute(self) -> list[UUID]:
        """Create pending scans and return the ids of the new ones."""
        companies = await self.company_repository.list_all(
            filters={"scan_enabled": True},
        )
        scan_ids: list[UUID] = []
        for company in companies:
            scan = None
            try:
                scan = await self.scan_repository.create(
                    Scan(company=company, status=ScanStatus.PENDING),
                )
            except IntegrityError:
                logger.info(
                    msg=f"Company {company.id} already has an "
                    "active scan; skipping",
                )
            if scan is not None:
                scan_ids.append(scan.id)
        return scan_ids
