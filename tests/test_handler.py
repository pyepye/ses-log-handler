import logging
import sys

import pytest

from ses_log_handler import SESHandler

from .fixtures import aws_env_vars, ses_handler  # NOQA: F401


def test_init_defaults(aws_env_vars):  # NOQA: F811
    sender = 'test@example.com'
    recipients = ['test@example.com']
    handler = SESHandler(
        sender=sender,
        recipients=recipients,
    )
    assert handler.sender
    assert handler.recipients
    assert handler.subject is None
    assert handler.access_key is None
    assert handler.secret_key is None
    assert handler.region is None


def test_init_args():
    sender = 'test@example.com'
    recipients = ['test@example.com']
    subject = 'Test subject'
    access_key = 'myaccesskey'
    secret_key = 'mysecretkey'
    region = 'eu-west-1'
    handler = SESHandler(
        sender=sender,
        recipients=recipients,
        subject=subject,
        access_key=access_key,
        secret_key=secret_key,
        region=region,
    )
    assert handler.sender == sender
    assert handler.recipients == recipients
    assert handler.subject == subject
    assert handler.access_key == access_key
    assert handler.secret_key == secret_key
    assert handler.region == region


def test_init_missing_required_args():
    with pytest.raises(TypeError) as error:
        SESHandler()
    assert '__init__() missing 2 required positional arguments' in str(error)
    assert "'sender'" in str(error)
    assert "'recipients'" in str(error)


def test_subject(mocker, freezer, ses_handler):  # NOQA: F811
    ses_handler.subject = 'Custom Subject'
    assert ses_handler.subject == ses_handler._subject(mocker.Mock())


def test_emit_basic_log_message(mocker, freezer, ses_handler):  # NOQA: F811
    freezer.move_to('2021-01-01T00:00:00')

    ses_client = mocker.patch.object(ses_handler, 'ses_client')
    logger = logging.getLogger()
    logger.addHandler(ses_handler)

    log_message = 'test'
    subject = f'{logging.getLevelName(ses_handler.level)}: {log_message}'
    message = f'''
From: {ses_handler.sender}
To: {', '.join(ses_handler.recipients)}
Subject: {subject}
Date: Fri, 01 Jan 2021 00:00:00 -0000

{log_message}
'''

    logger.error('test')

    ses_client.send_email.assert_called_once_with(
        Destination={'ToAddresses': ses_handler.recipients},
        Message={
            'Body': {'Text': {'Charset': 'UTF-8', 'Data': message}},
            'Subject': {'Charset': 'UTF-8', 'Data': subject},
        },
        Source=ses_handler.sender,
    )


def test_emit_stack_trace_log(mocker, freezer, ses_handler):  # NOQA: F811
    freezer.move_to('2021-01-01T00:00:00')

    ses_client = mocker.patch.object(ses_handler, 'ses_client')
    logger = logging.getLogger()
    logger.addHandler(ses_handler)

    log_message = 'A key was missing'
    subject = f'{logging.getLevelName(ses_handler.level)}: {log_message}'
    try:
        {'key': 'value'}['badkey']
    except KeyError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(log_message, exc_info=True)

    message = """
From: %s
To: %s
Subject: %s
Date: Fri, 01 Jan 2021 00:00:00 -0000

%s
Traceback (most recent call last):
  File "%s", line %s, in %s
    {'key': 'value'}['badkey']
%s: 'badkey'
""" % (
        ses_handler.sender,
        ', '.join(ses_handler.recipients),
        subject,
        log_message,
        exc_traceback.tb_frame.f_code.co_filename,
        exc_traceback.tb_lineno,
        exc_traceback.tb_frame.f_code.co_name,
        exc_type.__name__,
    )

    ses_client.send_email.assert_called_once_with(
        Destination={'ToAddresses': ses_handler.recipients},
        Message={
            'Body': {'Text': {'Charset': 'UTF-8', 'Data': message}},
            'Subject': {'Charset': 'UTF-8', 'Data': subject},
        },
        Source=ses_handler.sender,
    )
