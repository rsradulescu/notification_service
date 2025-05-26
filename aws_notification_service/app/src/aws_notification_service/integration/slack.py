"""
aws_notification_service.integration.slack
"""
from urllib import request
from urllib.request import Request
import json

from aws_notification_service.integration import ServiceIntegration


class SlackIntegration(ServiceIntegration):
    """SlackIntegration"""

    def send(self, destination, subject, message):
        """send"""
        req = Request(
            destination,
            json.dumps(
                    {
                        "blocks" : [
                            {
                                "type": "header",
                                "text": {
                                    "type": "plain_text",
                                    "text": subject
                                }
                            },
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": message
                                }
                            }
                        ]
                    }
            ).encode('utf-8'),
            {'Content-Type': 'application/json; charset=utf-8'}
        )
        response = request.urlopen(req)
        txt = response.read().decode("utf-8")
        if response.status != 200 or txt != "ok":
            raise Exception(f"Slack error: {response.status}, body {len(txt)}.")
        return response.headers["x-slack-unique-id"]
