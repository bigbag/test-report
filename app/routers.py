import logging
import os

from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import ValidationError as PydanticValidationError
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette_prometheus import metrics

from . import adapters
from . import entities as e
from . import exceptions, utils

logger = logging.getLogger("test-report")


router = APIRouter()


@router.get("/ping", response_model=e.PingResponse, tags=["system"])
def get_ping():
    """Healthcheck for load balancers L7"""
    return e.PingResponse()


@router.get("/health", response_model=e.HealthReport, tags=["system"])
async def get_status():
    """Healthcheck for dependencies services"""
    return e.HealthReport(user_info=await adapters.user_adapter.get_status())


@router.get("/exception", response_class=PlainTextResponse, tags=["system"])
def make_exception():
    1 / 0


@router.get("/metrics", name="Get service metrics for prometheus.", tags=["system"])
async def get_metrics(request: Request):
    return metrics(request)


@router.post(
    "/report",
    tags=["user"],
    response_class=PlainTextResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(utils.check_basic_auth)],
)
async def create_report(
    background_tasks: BackgroundTasks,
    source_file: UploadFile = File(...),
    recipients: str = Body(..., title="List of recipients, delimiter comma"),
):
    if source_file.content_type not in ["text/csv"]:
        raise exceptions.APIError(
            status.HTTP_400_BAD_REQUEST,
            message="Invalid document type, we support only csv",
        )

    try:
        info = e.ReportRecipients(recipients=recipients.split(","))
    except PydanticValidationError:
        raise exceptions.APIError(
            status.HTTP_400_BAD_REQUEST,
            message="Invalid list of recipients",
        )

    report = adapters.report_adapter.create(
        source_file=source_file.file, recipients=info.recipients
    )

    background_tasks.add_task(report.generate)
    return report.get_report_url(report.report_id)


@router.get("/report/{report_id}", tags=["user"])
async def get_report(report_id: str):
    def iterfile(path):
        with open(path, mode="rb") as f:
            yield from f

    report_path = adapters.report_adapter.get_report_path(report_id)
    if not os.path.exists(report_path):
        raise exceptions.APIError(
            status.HTTP_404_NOT_FOUND,
            message=f"Report with id '{report_id}' is not found",
        )

    response = StreamingResponse(iterfile(report_path), media_type="application/x-zip-compressed")
    response.headers["Content-Disposition"] = "attachment; filename=report.zip"
    return response
