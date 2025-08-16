from collections.abc import Iterable, Sequence
from contextlib import asynccontextmanager
from typing import Any, Generic, TypeVar

from tortoise import models
from tortoise.transactions import in_transaction

try:
    # Optional pagination integration
    from fastapi_pagination.ext.tortoise import paginate as tortoise_paginate

    _HAS_PAGINATION = True
except Exception:
    _HAS_PAGINATION = False

T = TypeVar("T", bound=models.Model)


class BaseRepository(Generic[T]):
    """
    Generic repository for Tortoise ORM models.
    Provides common CRUD operations, filtering, ordering, preloading and transactions.
    """

    model: type[T]
    database: str

    def __init__(self, model: type[T], database: str = "default") -> None:
        """
        Initialize the repository for a given Tortoise model.

        :param model: Tortoise model class
        :param database: Tortoise database name (connections config key)
        """
        self.model = model
        self.database = database

    # ---------- Query building helpers ----------

    def _apply_filters(self, qs, *, filters: dict[str, Any] | None) -> Any:
        """
        Apply Tortoise-style filters where keys support lookups (e.g., 'created_at__gte').
        """
        if not filters:
            return qs
        return qs.filter(**filters)

    def _apply_ordering(self, qs, *, order_by: Sequence[str] | None) -> Any:
        """
        Apply ordering. Use list like ['-created_at', 'status'].
        """
        if not order_by:
            return qs
        return qs.order_by(*order_by)

    def _apply_preloads(self, qs, *, select_related: Iterable[str] | None,
                        prefetch_related: Iterable[str] | None) -> Any:
        """
        Apply relation preloading:
        - select_related: FK joins (single-valued)
        - prefetch_related: reverse/many relations
        """
        if select_related:
            qs = qs.select_related(*select_related)
        if prefetch_related:
            qs = qs.prefetch_related(*prefetch_related)
        return qs

    # ---------- Transactions ----------

    @asynccontextmanager
    async def transaction(self):
        """
        Transaction context manager. Pass the `using_db=conn` to operations inside.
        """
        async with in_transaction(self.database) as conn:
            yield conn

    # ---------- Read operations ----------

    async def get_by_id(
            self,
            *,
            id: Any,
            select_related: Iterable[str] | None = None,
            prefetch_related: Iterable[str] | None = None,
            using_db=None,
    ) -> T | None:
        """
        Retrieve a single record by primary key.
        """
        qs = self.model.filter(id=id).using_db(using_db or self.database)
        qs = self._apply_preloads(qs, select_related=select_related, prefetch_related=prefetch_related)
        return await qs.first()

    async def get_one(
            self,
            *,
            filters: dict[str, Any] | None = None,
            order_by: Sequence[str] | None = None,
            select_related: Iterable[str] | None = None,
            prefetch_related: Iterable[str] | None = None,
            using_db=None,
    ) -> T | None:
        """
        Retrieve the first record matching filters and order_by.
        """
        qs = self.model.all().using_db(using_db or self.database)
        qs = self._apply_filters(qs, filters=filters)
        qs = self._apply_ordering(qs, order_by=order_by)
        qs = self._apply_preloads(qs, select_related=select_related, prefetch_related=prefetch_related)
        return await qs.first()

    async def list(
            self,
            *,
            filters: dict[str, Any] | None = None,
            order_by: Sequence[str] | None = None,
            limit: int | None = None,
            offset: int | None = None,
            select_related: Iterable[str] | None = None,
            prefetch_related: Iterable[str] | None = None,
            using_db=None,
    ) -> list[T]:
        """
        List records with optional filters, ordering, and classic pagination (limit/offset).
        """
        qs = self.model.all().using_db(using_db or self.database)
        qs = self._apply_filters(qs, filters=filters)
        qs = self._apply_ordering(qs, order_by=order_by)
        qs = self._apply_preloads(qs, select_related=select_related, prefetch_related=prefetch_related)
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
            using_db=None,
    ):
        """
        Return a Page[T] using fastapi-pagination (if installed).
        """
        if not _HAS_PAGINATION:
            raise RuntimeError("fastapi-pagination is not installed; use `list()` with limit/offset instead.")
        qs = self.model.all().using_db(using_db or self.database)
        qs = self._apply_filters(qs, filters=filters)
        qs = self._apply_ordering(qs, order_by=order_by)
        qs = self._apply_preloads(qs, select_related=select_related, prefetch_related=prefetch_related)
        return await tortoise_paginate(qs)

    async def count(self, *, filters: dict[str, Any] | None = None, using_db=None) -> int:
        """
        Count records matching filters.
        """
        qs = self.model.all().using_db(using_db or self.database)
        qs = self._apply_filters(qs, filters=filters)
        return await qs.count()

    async def exists(self, *, filters: dict[str, Any] | None = None, using_db=None) -> bool:
        """
        Check existence of records matching filters.
        """
        qs = self.model.all().using_db(using_db or self.database)
        qs = self._apply_filters(qs, filters=filters)
        return await qs.exists()

    # ---------- Write operations ----------

    async def create(self, *, values: dict[str, Any], using_db=None) -> T:
        """
        Create a single record.
        """
        instance = self.model(**values)
        await instance.save(using_db=using_db or self.database)
        return instance

    async def bulk_create(self, *, values: Iterable[dict[str, Any]], using_db=None, batch_size: int | None = None) -> \
            list[T]:
        """
        Bulk create records. Returns created instances (without PK roundtrip).
        """
        instances = [self.model(**val) for val in values]
        await self.model.bulk_create(instances, using_db=using_db or self.database, batch_size=batch_size)
        return instances

    async def update_by_id(self, *, id: Any, values: dict[str, Any], using_db=None) -> int:
        """
        Update a single record by primary key. Returns affected rows count.
        """
        return await self.model.filter(id=id).using_db(using_db or self.database).update(**values)

    async def update_where(self, *, filters: dict[str, Any], values: dict[str, Any], using_db=None) -> int:
        """
        Update all records matching filters. Returns affected rows count.
        """
        qs = self.model.filter(**(filters or {})).using_db(using_db or self.database)
        return await qs.update(**values)

    async def delete_by_id(self, *, id: Any, using_db=None) -> int:
        """
        Delete a single record by primary key. Returns affected rows count.
        """
        return await self.model.filter(id=id).using_db(using_db or self.database).delete()

    async def delete_where(self, *, filters: dict[str, Any], using_db=None) -> int:
        """
        Delete all records matching filters. Returns affected rows count.
        """
        return await self.model.filter(**(filters or {})).using_db(using_db or self.database).delete()
