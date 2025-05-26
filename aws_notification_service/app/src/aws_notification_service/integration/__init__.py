"""
aws_notification_service.integration
"""
from abc import ABCMeta, abstractmethod
from typing import Any


class ServiceIntegration(metaclass=ABCMeta) :
    """ServiceIntegration"""

    @abstractmethod
    def send(self, destination:str, subject:str, message:Any) :
        """send"""
