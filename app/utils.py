import secrets

from fastapi import Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from . import exceptions
from .conf import secret_settings

security = HTTPBasic()


def check_basic_auth(
    credentials: HTTPBasicCredentials = Depends(security),
):
    correct_username = secrets.compare_digest(
        credentials.username, secret_settings.basic_auth_username
    )
    correct_password = secrets.compare_digest(
        credentials.password,
        secret_settings.basic_auth_password.get_secret_value(),
    )
    if not (correct_username and correct_password):
        raise exceptions.APIError(status.HTTP_401_UNAUTHORIZED)
