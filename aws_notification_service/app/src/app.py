"""aws_notification_service.app"""
import os
import json
from aws_notification_service import AWSNotificationService

from aws_notification_service.integration.dummy import DummyIntegration
from aws_notification_service.integration.slack import SlackIntegration
from aws_notification_service.integration.mail import MailIntegration

notification_service = AWSNotificationService(
    channels = {
        "dummy" : DummyIntegration(),
        "slack" : SlackIntegration(),
        "mail" : MailIntegration(
            ses_sender = os.environ.get("SES_SENDER"),
            ses_conf_set = os.environ.get("SES_CONFIGURATION_SET"),
        ),
    },
    dst_param_prefix = os.environ.get("DST_PARAM_PREFIX"),
)

def notification_handler(event) :
    """notification_handler"""
    notification_report = notification_service.send( **event )
    print(json.dumps(notification_report.serialize()))
    return notification_report

def lambda_handler(event, context) : #pylint: disable=unused-argument
    """lambda_handler"""
    # SQS
    if "Records" in event:
        batch_item_failures = []
        for record in event["Records"]:
            notification_report = notification_handler( json.loads(record["body"]) )
            if not notification_report.success :
                batch_item_failures.append({"itemIdentifier": record["messageId"]})
        return {
            "batchItemFailures" : batch_item_failures
        }
    notification_report = notification_handler(event)
    return notification_report.serialize()
