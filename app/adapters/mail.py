import typing as t

from .. import interfaces as i


class MailAdapter(i.MailAdapter):
    def startup(
        self,
        mail_driver: i.MailDriver,
        default_sender: str = "no-reply@test.env",
    ):
        self._mail = mail_driver
        self._default_sender = default_sender

    def shutdown(self):
        self._mail.shutdown()

    def send_start_notitication(self, recipients: t.List[str], report_id: str):
        self._mail.send(
            sender=self._default_sender,
            recipients=recipients,
            subject="Report was processing",
            text=(f"We started to generate a report with id {report_id} "),
        )

    def send_finish_notitication(
        self, recipients: t.List[str], report_id: str, password: str, url: str
    ):
        self._mail.send(
            sender=self._default_sender,
            recipients=recipients,
            subject="Report was done",
            text=(
                f"Password for test report with id {report_id} "
                f"is {password}. \n"
                f"You can download report by link {url}"
            ),
        )


mail_adapter = MailAdapter()
