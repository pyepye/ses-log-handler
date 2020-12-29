from email.utils import formatdate
from logging import Handler, LogRecord, getLogger

from boto3 import client as boto3_client
from botocore.exceptions import ClientError

log = getLogger(__name__)


class SESHandler(Handler):
    """
    Log messages to email via Amazon SES
    """

    def __init__(
        self,
        sender: str,
        recipients: list,
        subject: str = None,
        access_key: str = None,
        secret_key: str = None,
        region: str = None,
    ):
        Handler.__init__(self)
        self.sender = sender
        self.recipients = recipients

        self.subject = subject

        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region

        if access_key and secret_key and region:
            self.ses_client = boto3_client(
                'ses',
                region_name=self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )
        else:
            self.ses_client = boto3_client('ses')

    def _subject(self, record: LogRecord):
        if self.subject:
            return self.subject

        message = record.getMessage()
        message = message.replace('\n', '\\n').replace('\r', '\\r')
        subject = f'{record.levelname}: {message}'
        return subject

    def _message(self, record: LogRecord):
        body = self.format(record)

        message = f'''
From: {self.sender}
To: {', '.join(self.recipients)}
Subject: {self._subject(record)}
Date: {formatdate()}

{body}
'''
        return message

    def emit(self, record):
        subject = self._subject(record)
        message = self._message(record)
        charset = 'UTF-8'
        try:
            response = self.ses_client.send_email(
                Destination={'ToAddresses': self.recipients},
                Message={
                    'Body': {'Text': {'Charset': charset, 'Data': message}},
                    'Subject': {'Charset': charset, 'Data': subject},
                },
                Source=self.sender,
            )
        except ClientError as e:
            log.debug(f'SES log failed - {e.response["Error"]["Message"]}')
        else:
            log.debug(f'SES log sent - MessageId: {response["MessageId"]}')
