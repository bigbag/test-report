import typing as t
from uuid import UUID

import httpx

from .. import entities as e
from .. import exceptions
from .. import interfaces as i
from . import rest_client


class UserInfoDriver(rest_client.RestClient, i.UserInfoDriver):
    dependency_name = "UserInfoClient"
    health_url: str = "/v1/ping"
    health_timeout: int

    def startup(self, auth_token: str = ""):
        headers = {
            "accept": "application/json",
            "Accept-Encoding": "gzip",
            "User-Agent": self.dependency_name,
        }
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        self.headers = headers

    async def get_profile(self, user_uid: UUID) -> e.PassportUser:
        try:
            resp = await self.send(
                request=self.build_request(
                    method="GET",
                    url=f"/profiles/{user_uid}",
                )
            )
        except exceptions.DependencyFailed:
            return e.PassportUser(user_uid=user_uid)

        return e.PassportUser(**resp.json())

    async def get_email(self, user_uid: UUID) -> str:
        try:
            resp = await self.send(
                request=self.build_request(
                    method="GET",
                    url=f"/profiles/{user_uid}/email",
                )
            )
        except exceptions.DependencyFailed:
            return ""

        return resp.json().get("email", "")

    async def get_phone(self, user_uid: UUID) -> str:
        try:
            resp = await self.send(
                request=self.build_request(
                    method="GET",
                    url=f"/profiles/{user_uid}/phone",
                )
            )
        except exceptions.DependencyFailed:
            return ""

        return resp.json().get("phone", "")

    async def get_sum_sub_documents(self, user_uid: UUID) -> t.List[e.SumSubDocument]:
        try:
            resp = await self.send(
                request=self.build_request(
                    method="GET",
                    url=f"/applicants/by_user_uid/{user_uid}",
                )
            )
        except exceptions.DependencyFailed:
            return []

        resp_data = resp.json().get("list", {}).get("items", [{}])

        VALID_REVIEW_ANSWER = "GREEN"
        added_document_types = set()
        result = []
        for item in resp_data:
            review_result = item.get("review", {}).get("reviewResult", {})
            if not (review_result.get("reviewAnswer", "") == VALID_REVIEW_ANSWER):
                continue

            raw_documents = item.get("info", {}).get("idDocs", [])
            for raw_document in raw_documents:
                document = e.SumSubDocument(**raw_document)
                if document.document_type in added_document_types:
                    continue

                added_document_types.add(document.document_type)
                result.append(document)

        return result


def init_driver(
    host: str,
    ssl_verify: bool = True,
    auth_token: str = "",
    timeout: int = 5,
) -> UserInfoDriver:
    user_info_driver = UserInfoDriver(
        base_url=host,
        verify=ssl_verify,
        timeout=httpx.Timeout(timeout=timeout),
    )
    user_info_driver.startup(auth_token)

    return user_info_driver
