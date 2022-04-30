import smtplib
import typing as t
from email.mime.text import MIMEText

from pydantic import SecretStr

from .. import interfaces as i


class MailDriver(i.MailDriver):
    def startup(
        self,
        host: str,
        port: str,
        username: str,
        password: SecretStr,
        use_tls: bool,
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._use_tls = use_tls

    def send(
        self,
        sender: str,
        recipients: t.List[str],
        subject: str,
        text: str,
    ):
        with smtplib.SMTP(host=self._host, port=self._port) as server:
            if self._use_tls:
                server.starttls()

            if self._username and self._password:
                server.login(self._username, self._password.get_secret_value())

            msg = MIMEText(text)
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = ", ".join(recipients)

            server.sendmail(
                from_addr=sender,
                to_addrs=recipients,
                msg=msg.as_string(),
            )


def init_driver(
    host: str,
    port: str,
    username: str,
    password: SecretStr,
    use_tls: bool,
) -> MailDriver:
    mail_driver = MailDriver()
    mail_driver.startup(
        host=host,
        port=port,
        username=username,
        password=password,
        use_tls=use_tls,
    )

    return mail_driver
