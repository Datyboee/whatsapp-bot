import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

GRAPH_URL = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"


@app.route("/", methods=["GET"])
def home():
    return "WOLFE TZ WhatsApp Bot is running!", 200


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def receive_webhook():
    data = request.get_json(silent=True) or {}
    print("=== WEBHOOK PAYLOAD ===", flush=True)
    print(data, flush=True)

    print("Webhook received:")
    print(data)

    try:
        entry = data.get("entry", [])

        for item in entry:
            for change in item.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])

                for message in messages:
                    sender = message.get("from")

                    if not sender:
                        continue

                    # Simple automatic reply
                    message_id = message.get("id")

                    send_typing(sender, message_id)

                    send_message(
                        sender,
                        "Habari! 👋 Karibu WOLFE TZ. "
                        "Nimepokea ujumbe wako. Nikusaidie nini?"
                    )

    except Exception as e:
        print("Error:", e)

    return "EVENT_RECEIVED", 200


def send_typing(recipient, message_id):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
        "typing_indicator": {
            "type": "text"
        }
    }

    response = requests.post(
        GRAPH_URL,
        headers=headers,
        json=payload,
        timeout=20
    )

    print("Typing response:", response.status_code, response.text)


def send_message(recipient, text):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {
            "body": text
        }
    }

    response = requests.post(
        GRAPH_URL,
        headers=headers,
        json=payload,
        timeout=20
    )

    print("WhatsApp response:", response.status_code, response.text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
