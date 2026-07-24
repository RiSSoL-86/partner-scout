from collections.abc import Sequence

from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class BaseRepository[ModelT: models.Model, PrimaryKeyT]:
    """Basic asynchronous CRUD operations for a Django model."""

    model: type[ModelT]

    async def get(self, primary_key: PrimaryKeyT) -> ModelT | None:
        """Return a model instance by its primary key or None."""
        try:
            return await self.model.objects.aget(  # type: ignore[no-any-return, attr-defined]
                pk=primary_key,
            )
        except ObjectDoesNotExist:
            return None

    async def list(
        self,
        order_by: Sequence[str] = ("pk",),
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[ModelT], int]:
        """Return a page of model instances and their total.

        ``order_by`` holds the ordering fields; ordering defaults to the
        primary key.
        """
        if limit < 1:
            raise ValueError("limit must be greater than zero")
        if offset < 0:
            raise ValueError("offset must be greater than or equal to zero")

        queryset = self.model.objects.all()  # type: ignore[attr-defined]
        total = await queryset.acount()
        queryset = queryset.order_by(*order_by)
        page = [
            instance async for instance in queryset[offset : offset + limit]
        ]
        return page, total

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
