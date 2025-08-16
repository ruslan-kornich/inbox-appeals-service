import inspect
import json
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config.logger import logger


class ApplicationError(Exception):
    """Base class for all application-specific exceptions."""

    def __init__(self, message: str, *, extra: str | None = None) -> None:
        """Initialize application error."""
        super().__init__(message)
        self.message = message
        log = f"{message!s}" + (f"\n{extra!s}" if extra else "")
        logger.error(log)

    def __str__(self) -> str:
        """Return the string representation."""
        return self.message


class BusinessError(Exception):
    """Exceptions related to business logic errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        """Initialize business logic error."""
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self) -> str:
        """Return the string representation."""
        return self.message


def raise_business_error(message: str, *, status_code: int | None = None) -> None:
    """Raise Business error exception."""
    kwargs = {}
    if status_code is not None:
        kwargs["status_code"] = status_code
    raise BusinessError(message, **kwargs)


async def business_exception_handler(request: Request, exc: BusinessError) -> JSONResponse:  # noqa: ARG001
    """FastAPI handler for business logic exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message},
    )


def catch_errors(wrapped: Callable[..., Any]) -> Callable[..., Any]:
    """
    Exception handling for business logic with extra info.
    """

    def get_json(param: Any) -> Any:
        """Return 'param' as json."""
        if isinstance(param, BaseModel):
            return param.model_dump_json()
        return json.dumps(param, default=str)

    async def wrapper(*args, **kwargs) -> Any:  # noqa: ANN002, ANN003
        try:
            if inspect.iscoroutinefunction(wrapped):
                return await wrapped(*args, **kwargs)
            return wrapped(*args, **kwargs)
        except BusinessError:
            raise
        except Exception as e:
            extra = None
            stack = traceback.extract_tb(e.__traceback__)
            frame = stack[-1] if stack else None
            if frame:
                file_path = Path(frame.filename)
                project_root = Path.cwd()
                try:
                    file_name = file_path.relative_to(project_root)
                except ValueError:
                    file_name = str(file_path)
                    file_name = (
                        "site-packages" + file_name.split("site-packages", 1)[-1]
                        if "site-packages" in file_name
                        else file_name
                    )
                line_num = frame.lineno
                method_name = wrapped.__name__
                if args and isinstance(args[0], object):
                    method_name = f"{args[0].__class__.__name__}.{wrapped.__name__}"

                # Serialize the arguments and keyword arguments
                json_args = [get_json(arg) for arg in args]
                json_kwargs = [f"{key}: {get_json(value)}" for key, value in kwargs.items()]
                # Remove 'self' if it's an object instance
                if args and isinstance(args[0], object):
                    json_args.pop(0)

                extra = f"Call: {method_name} ({file_name}: {line_num}).\nArgs: {','.join([*json_args, *json_kwargs])}"

            # Log with ApplicationError, then re-raise the original exception
            message = f"{type(e).__module__}.{type(e).__name__}: {e!s}"
            ApplicationError(message=message, extra=extra)
            raise

    return wrapper
