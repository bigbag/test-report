import logging
import typing as t

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

logger = logging.getLogger("test-report")

DEPENDENCY_FAILED_HTTP_CODE = 543

DEFAULT_EXCEPTION_CODE = "SERVER_ERROR"
EXCEPTION_CODES = {
    status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
    status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
    status.HTTP_403_FORBIDDEN: "FORBIDDEN",
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    DEPENDENCY_FAILED_HTTP_CODE: "FAILED_DEPENDENCY",
    status.HTTP_500_INTERNAL_SERVER_ERROR: DEFAULT_EXCEPTION_CODE,
}


class DependencyFailed(Exception):
    dependency_name: str
    message: str = "{self.dependency_name} is currently unavailable"
    public_message: str = "{self.dependency_name} is currently unavailable"
    details: t.Any = ""

    def __init__(
        self,
        message: t.Optional[str] = None,
        public_message: t.Optional[str] = None,
        details: t.Optional[str] = None,
        dependency_name: t.Optional[str] = None,
    ):

        if dependency_name is not None:
            self.dependency_name = dependency_name

        if details is not None:
            self.details = details

        if message is not None:
            self.message = message

        if public_message is not None:
            self.public_message = public_message

        if not getattr(self, "dependency_name", None):
            self.dependency_name = self.__class__.__name__

        # render templates
        self.public_message = self.public_message.format(self=self)
        self.message = self.message.format(self=self)
        super().__init__(self.message)


class APIError(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: t.Optional[str] = DEFAULT_EXCEPTION_CODE
    message: t.Optional[str] = None

    def __init__(
        self,
        status_code: t.Optional[int] = None,
        code: t.Optional[int] = None,
        message: t.Optional[str] = None,
        details: t.Optional[t.Any] = None,
    ):

        self.status_code = status_code or self.status_code
        self.code = code or EXCEPTION_CODES.get(status_code) or self.code
        if message is not None:
            self.message = message

        self.details = details
        super().__init__()

    def as_dict(self) -> t.Dict[str, t.Any]:

        return {
            "code": self.code,
            "message": str(self.message),
            "details": self.details,
        }


class ValidationFailed(APIError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "VALIDATION_FAILED"

    def set_details(self, details: t.List[t.Dict[str, t.Any]]):
        self.details = normalize_details(details)


def normalize_details(details: t.List[t.Dict[str, t.Any]]) -> t.List[t.Dict[str, t.Any]]:
    return [
        {
            "code": data["type"].upper(),
            "field": ".".join([loc for loc in data["loc"] if isinstance(loc, str)]),
            "message": data["msg"],
        }
        for data in details
    ]


async def base_exception_handler(_, exc) -> JSONResponse:
    if isinstance(exc, APIError):
        return JSONResponse(exc.as_dict(), status_code=exc.status_code)

    logger.error(str(exc))

    error = APIError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JSONResponse(error.as_dict(), status_code=error.status_code)


async def api_error_exception_handler(_, exc: APIError) -> JSONResponse:
    logger.info(exc.as_dict())
    return JSONResponse(exc.as_dict(), status_code=exc.status_code)


async def http_exception_handler(_, exc: HTTPException) -> JSONResponse:
    error = APIError(
        status_code=exc.status_code,
    )
    logger.info(error.as_dict())
    return JSONResponse(error.as_dict(), status_code=error.status_code)


async def validation_exception_handler(_, exc: RequestValidationError) -> JSONResponse:
    error = ValidationFailed()
    error.set_details(exc.errors())
    logger.info(error.as_dict())
    return JSONResponse(error.as_dict(), status_code=error.status_code)


async def dependency_exception_handler(_, exc: DependencyFailed) -> JSONResponse:
    content = {
        "code": EXCEPTION_CODES[DEPENDENCY_FAILED_HTTP_CODE],
        "message": exc.public_message,
        "details": exc.details,
    }
    logger.exception(exc)
    return JSONResponse(content, status_code=DEPENDENCY_FAILED_HTTP_CODE)


def setup(app_: FastAPI):
    app_.add_exception_handler(APIError, api_error_exception_handler)
    app_.add_exception_handler(HTTPException, http_exception_handler)
    app_.add_exception_handler(RequestValidationError, validation_exception_handler)
    app_.add_exception_handler(PydanticValidationError, validation_exception_handler)
    app_.add_exception_handler(DependencyFailed, dependency_exception_handler)
    app_.add_exception_handler(Exception, base_exception_handler)
