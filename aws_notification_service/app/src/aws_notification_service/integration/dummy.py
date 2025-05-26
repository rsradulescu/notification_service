"""
aws_notification_service.integration.dummy
"""
from aws_notification_service.integration import ServiceIntegration


class DummyIntegration(ServiceIntegration):
    """DummyIntegration"""

    def send(self, destination, subject, message):
        return print(f"{destination} - {subject} - {message}")
