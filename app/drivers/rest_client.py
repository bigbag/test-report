import logging
import time

import httpx
from starlette import status

from .. import exceptions

logger = logging.getLogger("test-report")


class RestClient(httpx.AsyncClient):
    dependency_name: str
    health_url: str
    health_timeout: int = 3  # sec
    health_success_status: int = status.HTTP_200_OK

    def raise_for_status(self, resp: httpx.Response):
        try:
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            logger.debug(f"resp:{resp.status_code}: {resp.text} " f"from {self.dependency_name}")
            raise exceptions.DependencyFailed(
                dependency_name=self.dependency_name, details=str(exc)
            )

    async def send(self, request: httpx.Request, **kwargs) -> httpx.Response:
        logger.debug(f"Request URL: {request.url}")
        logger.debug(f"Request method: {request.method}")
        logger.debug(f"Request POST data: {request.content.decode()}")
        logger.debug(f"Request headers: {request.headers}")

        start_time = time.monotonic()
        try:
            resp = await super().send(request, **kwargs)
        except httpx.HTTPError as exc:
            logger.info(exc)
            raise exceptions.DependencyFailed(
                dependency_name=self.dependency_name, details=str(exc)
            )

        logger.debug(f"Request time: {(time.monotonic() - start_time):.4f} sec")
        logger.debug(f"Response code: {resp.status_code}")
        logger.debug(f"Response headers: {resp.headers}")
        logger.debug(f"Response body: {str(resp.text)}")

        self.raise_for_status(resp)
        return resp

    async def healthcheck(self) -> bool:
        try:
            resp = await self.send(
                request=self.build_request(
                    method="GET",
                    url=self.health_url,
                    timeout=httpx.Timeout(timeout=self.health_timeout),
                ),
            )
        except httpx.HTTPError as e:
            logger.exception(e)
            return False

        return resp.status_code == self.health_success_status
