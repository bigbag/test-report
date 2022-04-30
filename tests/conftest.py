import pytest
from starlette.config import environ
from starlette.testclient import TestClient

from app.main import app

from tests import fixtures

environ["TESTING"] = "True"


@pytest.fixture
def client(mocker):
    mocker.patch("app.drivers.user_info.UserInfoDriver", fixtures.MockedUserInfoDriver)
    mocker.patch("app.drivers.mail.MailDriver", fixtures.MockMailDriver)
    mocker.patch("app.adapters.report_adapter", fixtures.MockedReportAdapter())
    with TestClient(app) as client:
        yield client
