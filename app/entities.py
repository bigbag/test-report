import typing as t
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class StringEnum(Enum):
    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self.value) == other
        return False

    def __hash__(self):
        return hash(str(self))


class SumSubDocument(BaseModel):
    document_type: str = Field(None, alias="idDocType")
    country: str = Field(None, alias="country")
    first_name: str = Field(None, alias="firstName")
    first_name_en: str = Field(None, alias="firstNameEn")
    middle_name: str = Field(None, alias="middleName")
    middle_name_en: str = Field(None, alias="middleNameEn")
    last_name: str = Field(None, alias="lastName")
    last_name_en: str = Field(None, alias="lastNameEn")
    issued_date: str = Field(None, alias="issuedDate")
    issue_authority: str = Field(None, alias="issueAuthority")
    valid_until: str = Field(None, alias="validUntil")
    number: str = Field(None, alias="number")
    dob: str = Field(None, alias="dob")
    place_of_birth: str = Field(None, alias="placeOfBirth")


class PassportUser(BaseModel):
    wl_id: t.Optional[str] = ""
    user_uid: UUID
    email: t.Optional[str] = ""
    phone: t.Optional[str] = ""
    country: t.Optional[str] = ""
    registration_date: t.Optional[str] = ""
    registration_platform: t.Optional[str] = ""
    language: t.Optional[str] = ""
    first_name: t.Optional[str] = ""
    last_name: t.Optional[str] = ""
    patronymic: t.Optional[str] = ""
    address: t.Optional[str] = ""
    date_of_birth: t.Optional[str] = ""


class User(PassportUser):
    sum_sub_documents: t.List[SumSubDocument] = None

    def get_flat_dict(self) -> t.Dict[str, t.Any]:
        result = {}
        for key, value in self:
            if key != "sum_sub_documents":
                result[key] = value
                continue

            if not self.sum_sub_documents:
                continue

            for document in self.sum_sub_documents:
                prefix = str(document.document_type).lower()
                for key, value in document:
                    if key == "document_type":
                        continue

                    result[f"{prefix}_{key}"] = value

        return result


class PingResponse(BaseModel):
    ping: str = "pong"


class HealthReport(BaseModel):
    user_info: bool


class ReportRecipients(BaseModel):
    recipients: t.Set[EmailStr]
