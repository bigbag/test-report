import json
import logging
import logging.config
import time
import typing as t
import uuid

import json_logging
from fastapi import FastAPI
from json_logging import JSONLogFormatter, JSONRequestLogFormatter


class CustomFormatter(JSONRequestLogFormatter):
    def _format_log_object(self, record, request_util):
        result = super()._format_log_object(record, request_util)
        result["request_id"] = result.pop("correlation_id")
        return result


def setup(app: FastAPI, app_id: str, logging_config: t.Dict[str, t.Any]):
    json_logging.CORRELATION_ID_GENERATOR = uuid.uuid4
    json_logging.COMPONENT_ID = app_id
    json_logging.COMPONENT_NAME = app.title
    json_logging.JSON_SERIALIZER = json.dumps

    json_logging.init_fastapi(enable_json=True, custom_formatter=JSONLogFormatter)
    json_logging.init_request_instrument(
        app,
        custom_formatter=CustomFormatter,
        exclude_url_patterns=[r"/ping", r"/health"],
    )

    logging.config.dictConfig(logging_config)
    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("uvicorn.error").disabled = True


class TimerLogger:
    def __init__(self):
        self.start_time = self._get_current_time()
        self.full_interval = 0
        self.info = []

    @staticmethod
    def _get_current_time():
        return time.monotonic()

    def add(self, name: str):
        interval = self._get_current_time() - self.start_time - self.full_interval
        self.full_interval += interval
        self.info.append(f"{name}: {interval:.4f} sec")

    def _get_result(self):
        self.info.append(f"full time: {self.full_interval:.4f} sec")
        return ", ".join(self.info)

    def __repr__(self):
        return self._get_result()

    def __str__(self):
        return self._get_result()
