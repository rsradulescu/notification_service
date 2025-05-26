"""
aws_notification_service.integration.mail
"""
import os
from boto3 import Session

from aws_notification_service.integration import ServiceIntegration

class MailIntegration(ServiceIntegration):
    """MailIntegration"""

    def __init__(self, ses_sender:str, ses_conf_set:str ):
        self.__aws_session_config = {}
        self.__ses_sender = ses_sender
        self.__ses_conf_set = ses_conf_set

    @property
    def aws_session(self):
        """
        aws_session
        """
        return Session(**self.__aws_session_config)

    def send(self, destination, subject, message):
        """send"""
        res = self.aws_session.client("ses").send_email(
            Source=self.__ses_sender,
            Destination={
                'ToAddresses': destination.split(";")
            },
            Message={
                'Subject': {
                    'Data': subject,
                },
                'Body': {
                    'Text': {
                        'Data': message,
                    },
                    'Html': {
                        'Data': message,
                    }
                }
            },
            ConfigurationSetName=self.__ses_conf_set
        )
        return res["MessageId"]
