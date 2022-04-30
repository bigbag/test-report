import asynctest
from fastapi import status
from requests.auth import HTTPBasicAuth


def test_pong(client):
    response = client.get("/ping")
    assert response.status_code == status.HTTP_200_OK
    assert response.text == '{"ping":"pong"}'


def test_health(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK, response.text

    response_data = response.json()
    assert "user_info" in response_data
    assert response_data["user_info"]


@asynctest.patch("app.routers.metrics")
def test_metrics(mock_metrics, client):
    mock_metrics.return_value = "TEST"
    response = client.get("/metrics")
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data == "TEST"


def test_create_report_with_out_basic_auth(client):
    with open("./tests/reports/source/good.csv", "r") as f:
        response = client.post(
            "/report",
            files={
                "source_file": ("filename", f, "text/csv"),
            },
            data={"recipients": ["test@test.env,demo@test.env"]},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_report_with_bad_file_type(client):
    with open("./tests/reports/source/good.csv", "r") as f:
        response = client.post(
            "/report",
            auth=HTTPBasicAuth("admin", "password"),
            files={"source_file": ("filename", f, "text/html")},
            data={"recipients": "test@test.env,demo@test.env"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_report_without_recipients(client):
    with open("./tests/reports/source/good.csv", "r") as f:
        response = client.post(
            "/report",
            auth=HTTPBasicAuth("admin", "password"),
            files={"source_file": ("filename", f, "text/csv")},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@asynctest.patch("fastapi.BackgroundTasks.add_task")
def test_create_report_with_good_source_report(mock_add_task, client):
    with open("./tests/reports/source/good.csv", "r") as f:
        response = client.post(
            "/report",
            auth=HTTPBasicAuth("admin", "password"),
            files={"source_file": ("filename", f, "text/csv")},
            data={"recipients": "test@test.env,demo@test.env"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert mock_add_task.called is True


def test_get_report_if_not_found(client):
    response = client.get("/report/232323")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text


def test_get_report_if_found(client):
    response = client.get("/report/164787269463")
    assert response.status_code == status.HTTP_200_OK, response.text
