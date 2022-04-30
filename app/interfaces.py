import tempfile
import typing as t
from uuid import UUID

from pydantic import SecretStr

from app import entities as e


class UserInfoDriver:
    def startup(self, auth_token: str):
        ...

    def shutdown(self):
        ...

    async def get_profile(self, user_uid: UUID) -> e.PassportUser:
        ...

    async def get_email(self, user_uid: UUID) -> str:
        ...

    async def get_phone(self, user_uid: UUID) -> str:
        ...

    async def get_sum_sub_documents(self, user_uid: UUID) -> t.List[e.SumSubDocument]:
        ...


class MailDriver:
    def startup(
        self,
        host: str,
        port: str,
        username: str,
        password: SecretStr,
        use_tls: bool,
    ):
        ...

    def shutdown(self):
        ...

    def send(
        self,
        sender: str,
        recipients: t.List[str],
        subject: str,
        text: str,
    ):
        ...


class UserAdapter:
    def startup(self, user_info_driver: UserInfoDriver, users_chunk_size: int):
        ...

    def shutdown(self):
        ...

    async def get_status(self) -> bool:
        ...

    async def get(self, user_uid: UUID) -> e.User:
        ...

    async def get_all(self, user_uids: t.List[UUID]) -> t.List[e.User]:
        ...


class ReportAdapter:
    @classmethod
    def startup(
        cls,
        user_adapter: UserAdapter,
        tmp_dir: str,
        service_address: str,
    ):
        ...

    def shutdown(self):
        ...

    @classmethod
    def create(
        self,
        source_file: tempfile.SpooledTemporaryFile,
        recipients: t.List[str],
    ):
        ...

    def get_report_path(self, report_id: str) -> str:
        ...

    def get_report_url(self, report_id: str) -> str:
        ...

    async def generate(self):
        ...


class MailAdapter:
    def startup(
        self,
        mail_driver: MailDriver,
        default_sender: str,
    ):
        ...

    def shutdown(self):
        ...

    def send_start_notitication(self, recipients: t.List[str], report_id: str):
        ...

    def send_finish_notitication(
        self, recipients: t.List[str], report_id: str, password: str, url: str
    ):
        ...
