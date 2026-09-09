import os
import requests
from flask import Flask, request

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "1385178644668054")

GRAPH_URL = f"https://graph.facebook.com/v26.0/{PHONE_NUMBER_ID}/messages"


@app.route("/", methods=["GET"])
def home():
    return "WOLFE TZ WhatsApp Bot is live", 200


@app.route("/webhook", methods=["POST"])
def receive_webhook():
    data = request.get_json(silent=True) or {}

    print("=== WEBHOOK PAYLOAD ===", flush=True)
    print(data, flush=True)

    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                for message in value.get("messages", []):
                    sender = message.get("from")
                    message_type = message.get("type")

                    print(
                        f"=== MESSAGE === sender={sender}, type={message_type}",
                        flush=True
                    )

                    if not sender:
                        print("NO SENDER FOUND", flush=True)
                        continue

                    if message_type == "text":
                        text = message.get("text", {}).get("body", "")
                        print(f"USER TEXT: {text}", flush=True)

                        send_typing(sender)

                        send_message(
                            sender,
                            "Habari! 👋 Karibu WOLFE TZ. "
                            "Nimepokea ujumbe wako. Nikusaidie nini?"
                        )

    except Exception as e:
        print(f"WEBHOOK ERROR: {type(e).__name__}: {e}", flush=True)

    return "EVENT_RECEIVED", 200


def send_typing(recipient):
    if not ACCESS_TOKEN:
        print("ERROR: ACCESS_TOKEN is missing", flush=True)
        return

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": None,
    }

    # Mark the incoming message as read.
    # Typing indicators are handled separately below when supported.
    try:
        response = requests.post(
            GRAPH_URL,
            headers=headers,
            json={
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": recipient
            },
            timeout=20
        )

        print(
            "Typing/read response:",
            response.status_code,
            response.text,
            flush=True
        )

    except Exception as e:
        print(
            f"Typing/read ERROR: {type(e).__name__}: {e}",
            flush=True
        )


def send_message(recipient, text):
    if not ACCESS_TOKEN:
        print("ERROR: ACCESS_TOKEN is missing", flush=True)
        return

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

    try:
        response = requests.post(
            GRAPH_URL,
            headers=headers,
            json=payload,
            timeout=20
        )

        print(
            "WhatsApp response:",
            response.status_code,
            response.text,
            flush=True
        )

    except Exception as e:
        print(
            f"WhatsApp SEND ERROR: {type(e).__name__}: {e}",
            flush=True
        )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 10000))
    )
