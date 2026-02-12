from __future__ import annotations

from dataclasses import dataclass
from email.message import EmailMessage
import smtplib


@dataclass(frozen=True)
class EmailSettings:
    host: str
    port: int
    username: str | None
    password: str | None
    sender: str
    use_tls: bool = True


class EmailSender:
    def send_email(self, recipient: str, subject: str, text_body: str, html_body: str | None = None) -> None:
        raise NotImplementedError


class SMTPEmailSender(EmailSender):
    def __init__(self, settings: EmailSettings) -> None:
        self.settings = settings

    def send_email(self, recipient: str, subject: str, text_body: str, html_body: str | None = None) -> None:
        msg = EmailMessage()
        msg["From"] = self.settings.sender
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(text_body)
        if html_body:
            msg.add_alternative(html_body, subtype="html")

        with smtplib.SMTP(self.settings.host, self.settings.port, timeout=15) as smtp:
            if self.settings.use_tls:
                smtp.starttls()
            if self.settings.username and self.settings.password:
                smtp.login(self.settings.username, self.settings.password)
            smtp.send_message(msg)


class InMemoryEmailSender(EmailSender):
    def __init__(self) -> None:
        self.sent: list[dict[str, str]] = []

    def send_email(self, recipient: str, subject: str, text_body: str, html_body: str | None = None) -> None:
        self.sent.append(
            {
                "recipient": recipient,
                "subject": subject,
                "text_body": text_body,
                "html_body": html_body or "",
            }
        )
