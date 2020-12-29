# SES log handler

Log messages to email via Amazon SES

Rate limiting and bouncing are currently not supported.

If you are using Django then this is also possible using [Django's AdminEmailHandler](https://docs.djangoproject.com/en/3.1/topics/logging/#id4) and [django-ses](https://github.com/django-ses/django-ses) which supports rate limiting via AWS_SES_AUTO_THROTTLE.


## Quick start

### Installation

```bash
pip install ses-log-handler
```


If you using IAM roles to get credentials for AWS or have the correct environment variables defined (see [Boto3 configuration guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html)) then you can simply set a `sender` and `recipients` addresses for the handler:

```python
import logging

logger = logging.getLogger(__name__)


ses_handler = SESHandler(
    sender='from@example.com',
    recipients=['to@example.com'],
)
ses_handler.setLevel(logging.ERROR)
logger.addHandler(ses_handler)
```

There is an example of how to configure the log hander using [`dictConfig()`](#dict-config) and [`fileConfig()`](#file-config)

*Note: It is advised you set the log level to either `CRITICAL` or `ERROR`. This will stop the reciver_mails from being spammed by logs and you incuring a large SES bill.*



## Configuration options

If you want to explicitly set the access, secret and region this can also be when instantiating the `SESHandler`.

It also possible to force the subject line to be the same for each email

```python
mail_handler = SESHandler(
    sender='from@example.com',
    recipients=('to@example.com'),
    access_key='<access-key>',
    secret_key='<secret-key>',
    region='<region>',
    subject='Error: Exception raised',
)
```


#### sender

Required: Who the log email should be sent from. The domain should be added and configured as a [verified sender domain](https://console.aws.amazon.com/ses/home?region=us-east-1#verified-senders-domain:)

#### recipients

Required: A list of recipients who should receive the log emails.

If your SES account only has "sandbox" access (see [SES dashboard](https://console.aws.amazon.com/ses/home?region=us-east-1#dashboard:)) these email addresses must be added as [verified sender email address](https://console.aws.amazon.com/ses/home?region=us-east-1#verified-senders-email:)


#### access_key

Optional: The AWS access key for a user who has access to send emails via SES.

It is [best practices for managing AWS access keys](https://docs.aws.amazon.com/general/latest/gr/aws-access-keys-best-practices.html) use instance roles instead of passing access keys to your application.

If the access_key argument is not provided then the SESHandler (which uses boto3) will fall back to getting credentials from either the instance role or environment variables. See the [boto3 credentials guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) for more information.


#### secret_key

Optional: The AWS secret key for a user who has access to send emails via SES.

It is [best practices for managing AWS access keys](https://docs.aws.amazon.com/general/latest/gr/aws-access-keys-best-practices.html) use instance roles instead of passing access keys to your application.

If the access_key argument is not provided then the SESHandler (which uses boto3) will fall back to getting credentials from either the instance role or environment variables. See the [boto3 credentials guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) for more information.

#### region

Optional: The AWS region which should be used to send emails via SES

By default the region that your application is running in will be used


#### subject

Optional: Force overrides the subject line to be the same for each email.

The default is `<log_level>: <message>`



## Configuration examples

The below examples both create a logging config which logs everything `ERROR` and above to SES and anything `WARNING` and below to the console.

### Dict config

```python
import logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'general': {
            'format': '%(asctime)s %(name)s.%(funcName)s %(levelname)s [%(lineno)d] %(message)s',  # NOQA: E501
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'general',
            'level': 'INFO',
        },
        'ses': {
            'class': 'ses_log_handler.SESHandler',
            'formatter': 'general',
            'level': 'ERROR',
            'sender': 'from@example.com',
            'recipients': ['to@example.com'],
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['ses', 'console'],
   }
}
logging.config.dictConfig(LOGGING)
```


### File config

```ini
[loggers]
keys=root

[handlers]
keys=sesHandler,consoleHandler

[formatters]
keys=generalFormatter

[logger_root]
level=INFO
handlers=sesHandler,consoleHandler

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=generalFormatter
args=(sys.stdout,)

[handler_sesHandler]
class=ses_log_handler.SESHandler
level=ERROR
formatter=generalFormatter
args=['from@example.com', ['to@example.com']]

[formatter_generalFormatter]
format=%(asctime)s %(name)s.%(funcName)s %(levelname)s [%(lineno)d] %(message)s
```

Then to load this config you can use
```python
import logging

logging.config.fileConfig(
    'logging.conf',
    disable_existing_loggers=False
)
```
