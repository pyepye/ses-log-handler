import logging

import pytest

from ses_log_handler import SESHandler


@pytest.fixture
def aws_env_vars(monkeypatch):
    """Set the USER env var to assert the behavior."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "fake-access-from-fixture")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "fake-secret-from-fixture")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture
def ses_handler(aws_env_vars):
    sender = 'test@example.com'
    recipients = ['test@example.com']
    handler = SESHandler(
        sender=sender,
        recipients=recipients,
    )
    handler.setLevel(logging.ERROR)
    return handler
