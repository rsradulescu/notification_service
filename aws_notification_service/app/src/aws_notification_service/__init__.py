"""
aws_notification_service
"""
import logging
from logging import Logger
from typing import List
from dataclasses import dataclass
from datetime import datetime, timezone

from boto3 import Session

from aws_notification_service.integration import ServiceIntegration

@dataclass
class NotificationReport :
    """NotificationReport"""

    # Metadata
    timestamp: int

    # Configuration
    target:str
    segment:str
    channel:str

    # Message details
    subject_length: int
    message_length: int

    # Destination details
    integration : str = None
    destination_length: int = None

    # Result
    request_id:str = None
    success:bool = None
    error:str = None

    def serialize(self) -> dict :
        """serialize"""
        return {
            "timestamp" : self.timestamp,
            "target": self.target,
            "segment": self.segment,
            "channel": self.channel,
            "subject_length": self.subject_length,
            "message_length": self.message_length,
            "integration": self.integration,
            "destination_length": self.destination_length,
            "request_id": self.request_id,
            "success": self.success,
            "error": self.error,
        }


class AWSNotificationService:
    """
    AWSNotificationService

    destination configuration
    - <prefix>/{target}/{channel}
    - <prefix>/{target}/{segment}/main_channel
    - <prefix>/{target}/{segment}/{channel}
    """

    def __init__(self, channels:dict, dst_param_prefix:str, log:Logger=None ):
        err = []

        self.__log = log or logging.getLogger(__name__)

        self.__channels = {}
        for k,v in channels.items() :
            if not isinstance(k, str) :
                err.append(f"Invalid channel name: {type(k)}")
            if not isinstance(v, ServiceIntegration) :
                err.append(f"Invalid channel integration: {type(k)}")
            if isinstance(k, str) and isinstance(v, ServiceIntegration) :
                self.__channels[k] = v

        self.__aws_session_config = {}
        self.__dst_param_prefix = dst_param_prefix

        if len(err) > 0 :
            raise ValueError( "AwsNotificationService.__init__: %s" % ( '\n'.join(err) ))

    @property
    def aws_session(self):
        """
        aws_session
        """
        return Session(**self.__aws_session_config)

    def _ssm_parameters(self, path) :
        config = {}
        for p in self.aws_session.client("ssm").get_paginator("get_parameters_by_path").paginate(
            Path=path, WithDecryption=True, Recursive=True
        ) :
            for param in p["Parameters"]:
                config[param["Name"]] = param["Value"]
        return config

    def get_destination(self, target:str, segment:str, channel:str):
        """
        get_destination
        """
        #if channel is not None :
        #    if segment is not None :
        #        parameter_name = f"/{self.__dst_param_prefix}/{target}/{segment}/{channel}"
        #    else :
        #        parameter_name = f"/{self.__dst_param_prefix}/{target}/{channel}"
        #    try :
        #        parameter = self.aws_session.client("ssm").get_parameter(
        #                Name=parameter_name,
        #                WithDecryption=True,
        #            )
        #        return channel, parameter["Parameter"]["Value"]
        #    except Exception as err :
        #        if (
        #            ( type(err).__module__ == "botocore.errorfactory" ) and
        #            ( type(err).__name__ == "ParameterNotFound" )
        #        ):
        #            return None, None
        #        else :
        #            raise err
        #return None, None
        target_config = self._ssm_parameters(f"/{self.__dst_param_prefix}/{target}")
        if f"/{self.__dst_param_prefix}/{target}/{segment}/{channel}" in target_config :
            return channel, target_config[f"/{self.__dst_param_prefix}/{target}/{segment}/{channel}"]

        if f"/{self.__dst_param_prefix}/{target}/{channel}" in target_config :
            return channel, target_config[f"/{self.__dst_param_prefix}/{target}/{channel}"]

        if f"/{self.__dst_param_prefix}/{target}/{segment}/default_channel" in target_config :
            _c = target_config[f'/{self.__dst_param_prefix}/{target}/{segment}/default_channel']
            return _c, target_config[f"/{self.__dst_param_prefix}/{target}/{segment}/{_c}"]

        if f"/{self.__dst_param_prefix}/{target}/default_channel" in target_config :
            _c = target_config[f'/{self.__dst_param_prefix}/{target}/default_channel']
            return _c, target_config[f"/{self.__dst_param_prefix}/{target}/{_c}"]

        return None, None

    def send(
            self,
            target:str=None, segment:str=None, channel:str=None,
            subject:str=None, message:str=None
            ):
        """send"""
        notification_report = NotificationReport(
            timestamp = datetime.now(timezone.utc).timestamp(),
            target=target,
            segment=segment,
            channel=channel,
            subject_length=len(subject or ""),
            message_length=len(message or ""),
        )
        try :
            integration, destination = self.get_destination(target, segment, channel)
            if destination is None :
                notification_report.destination_length = 0
                notification_report.integration = None
                notification_report.error = "Configuration not available."
                notification_report.success = False
            else :
                notification_report.destination_length = len(destination)
                notification_report.integration = integration
                if integration in self.__channels :
                    notification_report.request_id = self.__channels[integration].send(
                        destination = destination, subject = subject, message = message
                        )
                    notification_report.success = True
                else :
                    notification_report.success = False
                    notification_report.error = f"Integration {integration} not available."
        except Exception as err : #pylint: disable=broad-exception-caught
            notification_report.error = f"{type(err).__module__}.{type(err).__name__} - {str(err)}"
            notification_report.success = False
            self.__log.exception(f"Notification error: {notification_report.error}")

        return notification_report
