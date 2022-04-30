import tempfile
import typing as t
import uuid
from uuid import UUID

import httpx
from faker import Faker

from app import entities as e
from app.adapters import report
from app.drivers import mail, user_info

faker = Faker()


class MockMailDriver(mail.MailDriver):
    def send(
        self,
        sender: str,
        recipients: t.List[str],
        subject: str,
        text: str,
    ):
        ...


class MockedReportAdapter(report.ReportAdapter):
    @classmethod
    def create(
        cls,
        source_file: tempfile.SpooledTemporaryFile,
        recipients: t.List[str],
    ):
        self = cls()
        self.report_id = "164787269463"
        self.password = uuid.uuid4().hex
        self._recipients = recipients
        self._source_file = source_file
        return self


class MockedUserInfoDriver(user_info.UserInfoDriver):
    def __init__(self, base_url: str, verify: bool, timeout: httpx.Timeout):
        ...

    def startup(self, auth_token: str = ""):
        ...

    async def healthcheck(self) -> bool:
        return True

    async def get_profile(self, user_uid: UUID) -> e.PassportUser:
        return e.PassportUser(
            wl_id=UUID("8711b8aa-cc68-413a-8034-c2716a2ce14a"),
            user_uid=user_uid,
            email=faker.email(),
            phone=faker.phone_number(),
            country=faker.bank_country(),
            language=faker.language_name(),
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            patronymic=faker.name(),
            registration_date="2020-01-01 00:00:00",
        )

    async def get_email(self, user_uid: UUID) -> str:
        return faker.email()

    async def get_phone(self, user_uid: UUID) -> str:
        return faker.phone_number()

    async def get_sum_sub_documents(self, user_uid: UUID) -> t.List[e.SumSubDocument]:
        return [
            e.SumSubDocument(
                document_type=e.SumSubDocumentType.PASSPORT,
                country="",
                first_name=faker.first_name(),
                first_name_en=faker.first_name(),
                middle_name=faker.middle_name(),
                middle_name_en=faker.middle_name(),
                last_name=faker.last_name(),
                last_name_en=faker.last_name(),
                issued_date="2020-01-01 00:00:00",
                issue_authority="",
                valid_until="",
                number="",
                dob="",
                place_of_birth="",
            )
        ]
