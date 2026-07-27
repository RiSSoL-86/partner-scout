from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

if TYPE_CHECKING:
    from django.db.models.expressions import OrderBy


class BaseRepository[ModelT: models.Model, PrimaryKeyT]:
    """Basic asynchronous CRUD operations for a Django model."""

    model: type[ModelT]

    def get_queryset(
        self,
        filters: Mapping[str, object] | None = None,
        select_related: Sequence[str] = (),
        order_by: Sequence[str | OrderBy] = (),
    ) -> models.QuerySet[ModelT]:
        """Build a queryset from caller-supplied filters and joins."""
        queryset = self.model.objects.all()  # type: ignore[attr-defined]
        if filters:
            queryset = queryset.filter(**filters)
        if select_related:
            queryset = queryset.select_related(*select_related)
        if order_by:
            queryset = queryset.order_by(*order_by)
        return queryset  # type: ignore[no-any-return]

    async def get(self, primary_key: PrimaryKeyT) -> ModelT | None:
        """Return a model instance by its primary key or None."""
        try:
            return await self.model.objects.aget(  # type: ignore[no-any-return, attr-defined]
                pk=primary_key,
            )
        except ObjectDoesNotExist:
            return None

    async def find_one(
        self,
        filters: Mapping[str, object],
        select_related: Sequence[str] = (),
    ) -> ModelT | None:
        """Return the first instance matching the filters, or None."""
        queryset = self.get_queryset(filters, select_related)
        return await queryset.afirst()

    async def list_all(
        self,
        filters: Mapping[str, object] | None = None,
        select_related: Sequence[str] = (),
        order_by: Sequence[str | OrderBy] = (),
    ) -> list[ModelT]:
        """Return every instance matching the caller-supplied query."""
        queryset = self.get_queryset(filters, select_related, order_by)
        return [instance async for instance in queryset]

    async def list(
        self,
        filters: Mapping[str, object] | None = None,
        select_related: Sequence[str] = (),
        order_by: Sequence[str | OrderBy] = ("pk",),
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[ModelT], int]:
        """Return a page of matching instances and their total."""
        if limit < 1:
            raise ValueError("limit must be greater than zero")
        if offset < 0:
            raise ValueError("offset must be greater than or equal to zero")

        queryset = self.get_queryset(filters, select_related, order_by)
        total = await queryset.acount()
        page = [
            instance async for instance in queryset[offset : offset + limit]
        ]
        return page, total

    async def count(
        self,
        filters: Mapping[str, object] | None = None,
    ) -> int:
        """Return how many instances match the caller-supplied filters."""
        return await self.get_queryset(filters).acount()

    @staticmethod
    async def create(instance: ModelT) -> ModelT:
        """Persist a new model instance."""
        await instance.asave(force_insert=True)
        return instance

    async def update(
        self,
        primary_key: PrimaryKeyT,
        instance: ModelT,
    ) -> ModelT | None:
        """Replace a model instance identified by its primary key."""
        stored_instance = await self.get(primary_key)
        if stored_instance is None:
            return None

        instance.pk = stored_instance.pk
        await instance.asave(force_update=True)
        return instance

    async def delete(self, primary_key: PrimaryKeyT) -> None:
        """Delete a model instance identified by its primary key."""
        instance = await self.get(primary_key)
        if instance is not None:
            await instance.adelete()
