import pytest

from phd_search_agent.mailer import send_email, smtp_configured


class FakeSMTP:
    instances = []

    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.tls = False
        self.login_args = None
        self.message = None
        FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def starttls(self):
        self.tls = True

    def login(self, username, password):
        self.login_args = (username, password)

    def send_message(self, message):
        self.message = message


def test_smtp_configured(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example")
    monkeypatch.setenv("SMTP_FROM", "me@example.com")
    assert smtp_configured()
    monkeypatch.delenv("SMTP_FROM")
    assert not smtp_configured()


def test_send_email_requires_configuration(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_FROM", raising=False)
    with pytest.raises(RuntimeError):
        send_email(to="x@example.com", subject="Hi", body="Body")


def test_send_email_tls_and_login(monkeypatch):
    FakeSMTP.instances.clear()
    monkeypatch.setattr("phd_search_agent.mailer.smtplib.SMTP", FakeSMTP)
    monkeypatch.setenv("SMTP_HOST", "smtp.example")
    monkeypatch.setenv("SMTP_PORT", "2525")
    monkeypatch.setenv("SMTP_FROM", "me@example.com")
    monkeypatch.setenv("SMTP_USERNAME", "user")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    monkeypatch.setenv("SMTP_USE_TLS", "true")
    send_email(to="x@example.com", subject="Hi", body="Body")
    smtp = FakeSMTP.instances[-1]
    assert smtp.tls is True
    assert smtp.login_args == ("user", "secret")
    assert smtp.message["To"] == "x@example.com"


def test_send_email_without_tls_or_login(monkeypatch):
    FakeSMTP.instances.clear()
    monkeypatch.setattr("phd_search_agent.mailer.smtplib.SMTP", FakeSMTP)
    monkeypatch.setenv("SMTP_HOST", "smtp.example")
    monkeypatch.setenv("SMTP_FROM", "me@example.com")
    monkeypatch.setenv("SMTP_USERNAME", "")
    monkeypatch.setenv("SMTP_USE_TLS", "false")
    send_email(to="x@example.com", subject="Hi", body="Body")
    smtp = FakeSMTP.instances[-1]
    assert smtp.tls is False
    assert smtp.login_args is None
