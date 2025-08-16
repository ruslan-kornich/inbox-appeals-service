import uuid
from tortoise import fields, models


class UUIDPrimaryKeyMixin(models.Model):
    """
    Mixin that adds a UUID primary key field named 'id'.
    """
    id = fields.UUIDField(pk=True, default=uuid.uuid4)

    class Meta:
        abstract = True


class CreatedUpdatedFieldsMixin(models.Model):
    """
    Mixin that adds 'created_at' and 'updated_at' timestamp fields.
    Note: Timestamps are application-side; for DB-side defaults you would need migrations.
    """
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True
