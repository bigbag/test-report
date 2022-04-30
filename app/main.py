import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette_prometheus import PrometheusMiddleware

from . import adapters, drivers, exceptions, logger, routers
from .conf import LOGGING, secret_settings, settings
from .version import __version__


def init_app():
    app_ = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version=__version__,
        docs_url="/docs" if settings.docs_enable else None,
    )

    app_.add_middleware(PrometheusMiddleware)
    if settings.sentry_dsn and settings.requests_ca_bundle:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            ca_certs=settings.requests_ca_bundle,
        )
        app_.add_middleware(SentryAsgiMiddleware)

    logger.setup(app=app_, app_id=settings.app_id, logging_config=LOGGING)
    exceptions.setup(app_)
    app_.include_router(routers.router)

    app_.on_event("shutdown")(_on_shutdown)
    app_.on_event("startup")(_on_startup)

    return app_


def _on_startup():
    adapters.user_adapter.startup(
        user_info_driver=drivers.init_user_info_driver(
            host=settings.user_info_host,
            ssl_verify=settings.user_info_verify,
            auth_token=secret_settings.user_info_token,
            timeout=settings.user_info_timeout,
        ),
        users_chunk_size=settings.users_chunk_size,
        after_chunk_timeout=settings.after_chunk_timeout,
    )

    adapters.report_adapter.startup(
        user_adapter=adapters.user_adapter,
        tmp_dir=settings.tmp_dir,
        service_address=settings.service_address,
    )

    adapters.mail_adapter.startup(
        mail_driver=drivers.init_mail_driver(
            host=settings.email_host,
            port=settings.email_port,
            username=settings.email_username,
            password=settings.email_password,
            use_tls=settings.email_use_tls,
        ),
    )


def _on_shutdown():
    adapters.user_adapter.shutdown()
    adapters.report_adapter.shutdown()


app = init_app()
