from passlib.context import CryptContext

from app.config.settings import settings
from app.models import UserRole
from app.repositories.citizen_profiles_repository import CitizenProfileRepository
from app.repositories.users_repository import UserRepository
from app.schemas.auth import RegisterUserBody, AccessTokenResponse
from app.security.jwt import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(raw_password: str) -> str:
    """Hash a plaintext password."""
    return pwd_context.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hash."""
    return pwd_context.verify(raw_password, hashed_password)


class AuthService:
    """
    Handles user registration and login.
    """

    def __init__(self) -> None:
        """
        Initialize AuthService with user and profile repositories.
        """
        self.user_repo = UserRepository()
        self.profile_repo = CitizenProfileRepository()

    async def register_user(self, payload: RegisterUserBody) -> tuple[str, UserRole]:
        """
        Create a USER and its citizen profile inside a transaction.

        Returns:
            tuple[str, UserRole]: A tuple with user id and role.

        Raises:
            ValueError: If the email is already registered.

        """
        if await self.user_repo.exists(filters={"email": payload.email}):
            error_message = "Email already registered"
            raise ValueError(error_message)

        async with self.user_repo.transaction() as conn:
            user = await self.user_repo.create(
                values={
                    "email": payload.email,
                    "password_hash": hash_password(payload.password),
                    "role": UserRole.USER,
                },
                using_db=conn,
            )
            await self.profile_repo.create(
                values={
                    "user_id": user.id,
                    "inn": payload.inn,
                    "phone": payload.phone,
                    "first_name": payload.first_name,
                    "last_name": payload.last_name,
                    "middle_name": payload.middle_name,
                    "birth_date": payload.birth_date,
                },
                using_db=conn,
            )

        return str(user.id), user.role

    async def login(self, *, email: str, password: str) -> AccessTokenResponse:
        """
        Validate credentials and return JWT access token + user info.

        Raises:
            ValueError: If email or password is invalid.
        """
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        expires_in = settings.JWT_ACCESS_EXPIRES_MINUTES * 60
        token = create_access_token(subject=str(user.id), role=user.role.value,
                                    expires_minutes=settings.JWT_ACCESS_EXPIRES_MINUTES)

        return AccessTokenResponse(
            access_token=token,
            user_id=str(user.id),
            role=user.role.value,
            expires_in=expires_in,
        )