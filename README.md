# SES log handler

Log messages to email via Amazon SES


## Quick start


### Installation

```bash
pip install ses-log-handler
```

If you using IAM roles to get credentials for AWS or have the correct environmental variables defined (see [Boto3 configuration guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html)) then you can simply set a `sender` and `recipients` addresses for the handler:

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

*Note: It is advised you set the log level to either `CRITICAL` or `ERROR`. This will stop the reciver_mails from being spammed by logs and you incuring a large SES bill.*


If you want to explitily set the access, secret and region this can also be when instantiating the `SESHandler`.

```python
mail_handler = SESHandler(
    sender='from@example.com',
    recipients=('to@example.com'),
    access_key='<access-key>',
    secret_key='<secret-key>',
    region='<region>',
)
```
