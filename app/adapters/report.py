import logging
import os
import tempfile
import time
import typing as t
import uuid

import pandas as pd
import pyminizip
from pandas.core.frame import DataFrame

from .. import interfaces as i
from ..logger import TimerLogger
from .mail import mail_adapter

logger = logging.getLogger("test-report")


class ReportAdapter(i.ReportAdapter):
    @classmethod
    def startup(
        cls,
        user_adapter: i.UserAdapter,
        tmp_dir: str,
        service_address: str,
    ):
        cls._user_adapter = user_adapter
        cls._tmp_dir = tmp_dir
        cls._service_address = service_address

    def shutdown(self):
        ...

    @classmethod
    def create(
        cls,
        source_file: tempfile.SpooledTemporaryFile,
        recipients: t.List[str],
    ):
        self = cls()
        self.report_id = str(int(time.time() * 100))
        self.password = uuid.uuid4().hex
        self._recipients = recipients
        self._source_file = source_file
        return self

    def get_report_path(self, report_id: str) -> str:
        return os.path.join(self._tmp_dir, f"report_{report_id}.zip")

    def get_report_url(self, report_id: str) -> str:
        return f"{self._service_address}/report/{report_id}"

    def _read_source_report(self):
        return pd.read_csv(
            self._source_file,
            index_col=False,
        )

    def _save_zip_file(self, df: DataFrame):
        COMPRESS_LEVEL = 1
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "report.xls")

            writer = pd.ExcelWriter(path, engine="xlsxwriter")
            df.to_excel(writer, index=False)
            writer.save()

            pyminizip.compress(
                path,
                None,
                self.get_report_path(self.report_id),
                self.password,
                COMPRESS_LEVEL,
            )

    async def generate(self):
        logger.info(f"Start report generation, id {self.report_id}")

        time_logger = TimerLogger()
        source_report = self._read_source_report()
        time_logger.add("get source report")

        mail_adapter.send_start_notitication(recipients=self._recipients, report_id=self.report_id)

        info = []
        fields = set()
        users = await self._user_adapter.get_all(user_uids=source_report["user_uid"])
        time_logger.add("get user info")

        for user in users:
            user_info = user.get_flat_dict()
            fields |= set(user_info.keys())
            info.append(user_info)

        df = pd.DataFrame(
            info,
            columns=fields,
        )

        result = pd.concat([source_report, df], axis=1)
        result = result.loc[:, ~result.columns.duplicated()]

        time_logger.add("make result report")

        self._save_zip_file(result)
        time_logger.add("create zip archive")

        mail_adapter.send_finish_notitication(
            recipients=self._recipients,
            report_id=self.report_id,
            password=self.password,
            url=self.get_report_url(self.report_id),
        )

        logger.info(f"Report generation, id {self.report_id}, " f"full timeline: {time_logger}")


report_adapter = ReportAdapter()
