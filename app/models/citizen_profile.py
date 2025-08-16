from tortoise import fields
from .mixins import UUIDPrimaryKeyMixin, CreatedUpdatedFieldsMixin


class CitizenProfile(UUIDPrimaryKeyMixin, CreatedUpdatedFieldsMixin):
    """
    Profile data required by the spec for end-users (role=USER).
    Kept separate from 'User' so staff/admin accounts do not require citizen fields.
    """
    user = fields.OneToOneField(
        "models.User",
        related_name="citizen_profile",
        on_delete=fields.OnDelete.CASCADE,
    )

    # Required personal fields (per spec)
    inn = fields.CharField(max_length=32, index=True)  # Indexed for faster lookups
    phone = fields.CharField(max_length=32, index=True)  # Indexed for faster lookups
    first_name = fields.CharField(max_length=80)
    last_name = fields.CharField(max_length=80)
    middle_name = fields.CharField(max_length=80, null=True)  # Optional
    birth_date = fields.DateField(index=True)

    class Meta:
        table = "auth_citizen_profile"
        # user is OneToOne → implicit unique index; add helpful composite for filters if needed
        # unique_together / indexes can be extended later if business decides inn/phone must be unique
        indexes = ("inn", "phone", "birth_date")

    def __str__(self) -> str:
        return f"CitizenProfile<{self.id} user={self.user.id}>"
