import asyncio
import logging
import typing as t
from uuid import UUID

from .. import entities as e
from .. import interfaces as i

logger = logging.getLogger("test-report")


class UserAdapter(i.UserAdapter):
    def startup(
        self,
        user_info_driver: i.UserInfoDriver,
        users_chunk_size: int,
        after_chunk_timeout: int,
    ):
        self._user_info = user_info_driver
        self._users_chunk_size = users_chunk_size
        self._after_chunk_timeout = 1  # sec

    def shutdown(self):
        self._user_info.shutdown()

    async def get_status(self) -> bool:
        return await self._user_info.healthcheck()

    async def get(self, user_uid: UUID) -> e.User:
        # return e.User(user_uid=user_uid)
        (passport_user, email, phone, sum_sub_documents,) = await asyncio.gather(
            self._user_info.get_profile(user_uid),
            self._user_info.get_email(user_uid),
            self._user_info.get_phone(user_uid),
            self._user_info.get_sum_sub_documents(user_uid),
        )
        user = e.User.parse_obj(passport_user)
        user.email = email
        user.phone = phone
        user.sum_sub_documents = sum_sub_documents

        return user

    async def get_all(self, user_uids: t.List[UUID]) -> t.List[e.User]:
        logger.info(f"Get user info for {len(user_uids)} users")
        chunks = [
            user_uids[x : x + self._users_chunk_size]
            for x in range(0, len(user_uids), self._users_chunk_size)
        ]

        result = []
        i = 1
        for chunk in chunks:
            logger.info(f"Get info for {i} chunk, of users")
            result += await asyncio.gather(*[self.get(user_uuid) for user_uuid in chunk])
            i += 1

        return result


user_adapter = UserAdapter()
