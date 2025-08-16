
from collections.abc import AsyncIterator, Iterable, Sequence
from contextlib import asynccontextmanager
from typing import Any

from tortoise import models
from tortoise.backends.base.client import BaseDBAsyncClient
from tortoise.queryset import QuerySet
from tortoise.transactions import in_transaction

try:
    # Optional pagination integration
    from fastapi_pagination.ext.tortoise import paginate as tortoise_paginate

    _HAS_PAGINATION = True
except Exception:
    _HAS_PAGINATION = False

PAGINATION_NOT_INSTALLED_MSG = (
    "fastapi-pagination is not installed; use `list_records()` with limit/offset instead."
)


class BaseRepository[T: models.Model]:
    """
    Generic repository for Tortoise ORM models.

    Provides common CRUD operations, filtering, ordering, preloading, and transactions.
    """

    model: type[T]

    def __init__(self, model: type[T]) -> None:
        """
        Initialize the repository for a given Tortoise model.

        :param model: Tortoise model class.
        """
        self.model = model

    # ---------- Query building helpers ----------

    def _apply_filters(self, qs: QuerySet[T], *, filters: dict[str, Any] | None) -> QuerySet[T]:
        """
        Apply filters to a QuerySet.

        Keys support Tortoise-style lookups (e.g., 'created_at__gte').
        """
        if not filters:
            return qs
        return qs.filter(**filters)

    def _apply_ordering(self, qs: QuerySet[T], *, order_by: Sequence[str] | None) -> QuerySet[T]:
        """
        Apply ordering to a QuerySet.

        Use a sequence like ['-created_at', 'status'].
        """
        if not order_by:
            return qs
        return qs.order_by(*order_by)

    def _apply_preloads(
        self,
        qs: QuerySet[T],
        *,
        select_related: Iterable[str] | None,
        prefetch_related: Iterable[str] | None,
    ) -> QuerySet[T]:
        """
        Apply relation preloading.

        - select_related: FK joins (single-valued).
        - prefetch_related: reverse/many relations.
        """
        if select_related:
            qs = qs.select_related(*select_related)
        if prefetch_related:
            qs = qs.prefetch_related(*prefetch_related)
        return qs

    # ---------- Transactions ----------

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[BaseDBAsyncClient]:
        """
        Provide an async transaction context manager.

        Yields a DB client (BaseDBAsyncClient). Pass this client into repository
        methods via the 'using_db' argument.
        """
        async with in_transaction() as conn:
            yield conn

    # ---------- Read operations ----------

    async def get_by_id(
        self,
        *,
        pk: Any,
        select_related: Iterable[str] | None = None,
        prefetch_related: Iterable[str] | None = None,
        using_db: BaseDBAsyncClient | None = None,
    ) -> T | None:
        """
        Retrieve a single record by primary key.
        """
        qs: QuerySet[T] = self.model.filter(id=pk)
        if using_db is not None:
            qs = qs.using_db(using_db)

        qs = self._apply_preloads(
            qs,
            select_related=select_related,
            prefetch_related=prefetch_related,
        )
        return await qs.first()

    async def get_one(
        self,
        *,
        filters: dict[str, Any] | None = None,
        order_by: Sequence[str] | None = None,
        select_related: Iterable[str] | None = None,
        prefetch_related: Iterable[str] | None = None,
        using_db: BaseDBAsyncClient | None = None,
    ) -> T | None:
        """
        Retrieve the first record matching filters and ordering.
        """
        qs: QuerySet[T] = self.model.all()
        if using_db is not None:
            qs = qs.using_db(using_db)

        qs = self._apply_filters(qs, filters=filters)
        qs = self._apply_ordering(qs, order_by=order_by)
        qs = self._apply_preloads(
            qs,
            select_related=select_related,
            prefetch_related=prefetch_related,
        )
        return await qs.first()

    async def list_records(  # noqa: PLR0913
        self,
        *,
        filters: dict[str, Any] | None = None,
        order_by: Sequence[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        select_related: Iterable[str] | None = None,
        prefetch_related: Iterable[str] | None = None,
        using_db: BaseDBAsyncClient | None = None,
    ) -> list[T]:
        """
        List records with optional filters, ordering, and classic pagination.

        Supports `limit`/`offset` pagination when fastapi-pagination is not used.
        """
        qs: QuerySet[T] = self.model.all()
        if using_db is not None:
            qs = qs.using_db(using_db)

        qs = self._apply_filters(qs, filters=filters)
        qs = self._apply_ordering(qs, order_by=order_by)
        qs = self._apply_preloads(
            qs,
            select_related=select_related,
            prefetch_related=prefetch_related,
        )
        if offset:
            qs = qs.offset(offset)
        if limit:
            qs = qs.limit(limit)
        return await qs

    async def paginate(
        self,
        *,
        filters: dict[str, Any] | None = None,
        order_by: Sequence[str] | None = None,
        select_related: Iterable[str] | None = None,
        prefetch_related: Iterable[str] | None = None,
        using_db: BaseDBAsyncClient | None = None,
    ) -> Any:
        """
        Return a paginated response using fastapi-pagination.
        """
        if not _HAS_PAGINATION:
            msg = PAGINATION_NOT_INSTALLED_MSG
            raise RuntimeError(msg)

        qs: QuerySet[T] = self.model.all()
        if using_db is not None:
            qs = qs.using_db(using_db)

        qs = self._apply_filters(qs, filters=filters)
        qs = self._apply_ordering(qs, order_by=order_by)
        qs = self._apply_preloads(
            qs,
            select_related=select_related,
            prefetch_related=prefetch_related,
        )
        return await tortoise_paginate(qs)

    async def count(self, *, filters: dict[str, Any] | None = None, using_db: BaseDBAsyncClient | None = None) -> int:
        """
        Count records matching filters.
        """
        qs: QuerySet[T] = self.model.all()
        if using_db is not None:
            qs = qs.using_db(using_db)

        qs = self._apply_filters(qs, filters=filters)
        return await qs.count()

    async def exists(
        self,
        *,
        filters: dict[str, Any] | None = None,
        using_db: BaseDBAsyncClient | None = None,
    ) -> bool:
        """
        Check whether any record exists that matches the provided filters.
        """
        qs: QuerySet[T] = self.model.all()
        if using_db is not None:
            qs = qs.using_db(using_db)

        qs = self._apply_filters(qs, filters=filters)
        return await qs.exists()

    # ---------- Write operations ----------

    async def create(self, *, values: dict[str, Any], using_db: BaseDBAsyncClient | None = None) -> T:
        """
        Create a single record and return the saved instance.
        """
        instance = self.model(**values)
        await instance.save(using_db=using_db)
        return instance

    async def bulk_create(
        self,
        *,
        values: Iterable[dict[str, Any]],
        using_db: BaseDBAsyncClient | None = None,
        batch_size: int | None = None,
    ) -> list[T]:
        """
        Bulk create records and return the created instances.

        Primary keys may be generated without per-row roundtrip depending on the backend.
        """
        instances = [self.model(**val) for val in values]
        await self.model.bulk_create(
            instances,
            using_db=using_db,
            batch_size=batch_size,
        )
        return instances

    async def update_by_id(
        self,
        *,
        pk: Any,
        values: dict[str, Any],
        using_db: BaseDBAsyncClient | None = None,
    ) -> int:
        """
        Update a single record by primary key and return the affected rows count.
        """
        qs: QuerySet[T] = self.model.filter(id=pk)
        if using_db is not None:
            qs = qs.using_db(using_db)
        return await qs.update(**values)

    async def update_where(
        self,
        *,
        filters: dict[str, Any],
        values: dict[str, Any],
        using_db: BaseDBAsyncClient | None = None,
    ) -> int:
        """
        Update all records matching filters and return the affected rows count.
        """
        qs: QuerySet[T] = self.model.filter(**(filters or {}))
        if using_db is not None:
            qs = qs.using_db(using_db)
        return await qs.update(**values)

    async def delete_by_id(self, *, pk: Any, using_db: BaseDBAsyncClient | None = None) -> int:
        """
        Delete a single record by primary key and return the affected rows count.
        """
        qs: QuerySet[T] = self.model.filter(id=pk)
        if using_db is not None:
            qs = qs.using_db(using_db)
        return await qs.delete()

    async def delete_where(self, *, filters: dict[str, Any], using_db: BaseDBAsyncClient | None = None) -> int:
        """
        Delete all records matching filters and return the affected rows count.
        """
        qs: QuerySet[T] = self.model.filter(**(filters or {}))
        if using_db is not None:
            qs = qs.using_db(using_db)
        return await qs.delete()
