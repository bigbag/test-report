import os
from typing import Optional

from pydantic import AnyUrl, BaseSettings, Field, SecretStr
from pydantic_vault import vault_config_settings_source


class Settings(BaseSettings):
    app_id: str = "test-report"
    app_name: str = "Test report service"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    debug: bool = False
    docs_enable: bool = True

    requests_ca_bundle: str = ""

    email_host: str
    email_port: str
    email_use_tls: bool = False
    email_username: str = ""
    email_password: SecretStr = None

    service_address: str
    tmp_dir: str = "./tmp"
    users_chunk_size: int = 20
    after_chunk_timeout: int = 1  # sec

    vault_enable: bool = False
    vault_url: Optional[AnyUrl]
    vault_namespace: Optional[str]
    vault_kubernetes_role: Optional[str]

    user_info_host: AnyUrl
    user_info_verify: bool = True
    user_info_timeout: int = 5  # sec

    log_level: str = "INFO"
    sentry_dsn: str = ""
    graylog_enable: bool = False
    graylog_host: Optional[str]
    graylog_port: Optional[int]
    graylog_compress: Optional[bool] = True


settings = Settings()


class SecretSettings(BaseSettings):
    user_info_token: Optional[str] = Field(
        None,
        vault_secret_path=settings.vault_namespace,
        vault_secret_key="USER_INFO_TOKEN",
    )

    basic_auth_username: str = Field(
        ...,
        vault_secret_path=settings.vault_namespace,
        vault_secret_key="BASIC_AUTH_USERNAME",
    )
    basic_auth_password: SecretStr = Field(
        ...,
        vault_secret_path=settings.vault_namespace,
        vault_secret_key="BASIC_AUTH_PASSWORD",
    )

    class Config:
        vault_url: str = settings.vault_url
        vault_kubernetes_role: str = settings.vault_kubernetes_role

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            if settings.vault_enable:
                return (vault_config_settings_source,)
            return (env_settings,)


secret_settings = SecretSettings()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {},
    "handlers": {
        "console": {
            "level": settings.log_level,
            "class": "logging.StreamHandler",
        },
        "graylog": {
            "level": settings.log_level,
            "class": "pygelf.handlers.GelfUdpHandler",
            "host": settings.graylog_host,
            "port": settings.graylog_port,
            "compress": str(settings.graylog_compress),
            "_environment": "SECENV",
            "_app_name": settings.app_id,
            "include_extra_fields": True,
            "_container_id": os.getenv("HOSTNAME"),
            "_service": "none",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "graylog"] if settings.graylog_enable else ["console"],
            "level": settings.log_level,
        },
    },
}
