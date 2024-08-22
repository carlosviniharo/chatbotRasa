# whatsapp_connector.py

from rasa.core.channels.channel import InputChannel, OutputChannel, UserMessage
from sanic import Blueprint, response
from sanic.request import Request
from typing import Text, Dict, Any, Optional, List
from sanic.response import text

import requests
import json
import logging

logger = logging.getLogger(__name__)

class WhatsAppOutput(OutputChannel):
    """Output channel for WhatsApp Cloud API"""

    def __init__(self, access_token: Text, phone_number_id: Text) -> None:
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.api_url = f"https://graph.facebook.com/v13.0/{phone_number_id}/messages"

    async def send_text_message(
            self, 
            recipient_id: Text, 
            message: Text, 
            **kwargs: Any) -> None:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "text",
            "text": {
                "body": message
            }
        }
        response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
        logger.debug(f"WhatsApp API response: {response.status_code}, {response.text}")

    async def send_batch_messages(
            self, recipient_messages: List[Dict[Text, Any]]) -> None:
        """Send a batch of messages to different recipients."""
        for entry in recipient_messages:
            recipient_id = entry["recipient_id"]
            message = entry["message"]
            await self.send_text_message(recipient_id, message)
    

    async def send_custom_json(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        """Send custom json dict."""
        json_message.setdefault("messaging_product", "whatsapp")
        json_message.setdefault("recipient_type", "individual")
        json_message.setdefault("to", recipient_id)

        response = requests.post(self.api_url, headers=headers, data=json.dumps(json_message))
        logger.debug(f"WhatsApp API response: {response.status_code}, {response.text}")

class WhatsAppInput(InputChannel):
    """Custom input channel for WhatsApp Cloud API"""

    def __init__(
            self, 
            access_token: Text, 
            phone_number_id: 
            Text) -> None:
        self.access_token = access_token
        self.phone_number_id = phone_number_id

    @classmethod
    def name(cls) -> Text:
        return "whatsapp_cloud"

    @classmethod
    def from_credentials(cls, credentials: Optional[Dict[Text, Any]]) -> InputChannel:
        if not credentials:
            cls.raise_missing_credentials_exception()

        return cls(
            access_token=credentials.get("access_token"),
            phone_number_id=credentials.get("phone_number_id")
        )

    def blueprint(self, on_new_message):
            whatsapp_webhook = Blueprint("whatsapp_webhook", __name__)

            @whatsapp_webhook.route("/", methods=["GET"])
            async def verify(request: Request) -> Any:
                mode = request.args.get("hub.mode")
                token = request.args.get("hub.verify_token")
                challenge = request.args.get("hub.challenge")
                verify_token = "0c4b2d1ef9a8cade887f5acd2915c761b601dc87ec5093677566bcf5cdceea79"

                if mode == "subscribe" and token == verify_token:
                    return text(challenge)
                else:
                    return text("Verification token mismatch", status=403)
            @whatsapp_webhook.route("/", methods=["POST"])
            async def receive(request: Request) -> Any:
                payload = request.json
                logger.debug(f"Received WhatsApp payload: {payload}")

                if "messages" in payload["entry"][0]["changes"][0]["value"]:
                    for message in payload["entry"][0]["changes"][0]["value"]["messages"]:
                        sender_id = message["from"]
                        
                        # Determine message type
                        message_type = message.get("type")

                        # Handle text messages
                        if message_type == "text":
                            text = message.get("text", {}).get("body", "")
                            await on_new_message(
                                UserMessage(text, WhatsAppOutput(self.access_token, self.phone_number_id), sender_id)
                            )
                        
                        # Handle interactive messages (e.g., button replies)
                        elif message_type == "interactive":
                            # Process button replies
                            interactive = message.get("interactive", {})
                            button_reply = interactive.get("button_reply", {})
                            button_id = button_reply.get("id")
                            button_title = button_reply.get("title")

                            # Optionally, map button IDs to specific actions or texts
                            text = f"{button_title}"
                            await on_new_message(
                                UserMessage(text, WhatsAppOutput(self.access_token, self.phone_number_id), sender_id)
                            )
                        
                        # Add handling for other message types as needed
                        # For example: images, documents, etc.
                        else:
                            logger.debug(f"Unhandled message type: {message_type}")

                return response.json({"status": "received"})

            return whatsapp_webhook
