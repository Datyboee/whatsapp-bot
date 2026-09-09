import os
import requests
from flask import Flask, request

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "1385178644668054")

GRAPH_URL = (
    f"https://graph.facebook.com/v26.0/"
    f"{PHONE_NUMBER_ID}/messages"
)


@app.route("/", methods=["GET"])
def home():
    return "WOLFE TZ WhatsApp Bot is LIVE 🤖", 200


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
        print("SEND ERROR:", str(e), flush=True)


def mark_as_read(message_id):
    if not ACCESS_TOKEN:
        return

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }

    try:
        response = requests.post(
            GRAPH_URL,
            headers=headers,
            json=payload,
            timeout=20
        )

        print(
            "Read response:",
            response.status_code,
            response.text,
            flush=True
        )

    except Exception as e:
        print("READ ERROR:", str(e), flush=True)


@app.route("/webhook", methods=["POST"])
def receive_webhook():
    data = request.get_json(silent=True) or {}

    print("=== WEBHOOK PAYLOAD ===", flush=True)
    print(data, flush=True)

    try:
        for entry in data.get("entry", []):

            for change in entry.get("changes", []):

                value = change.get("value", {})

                messages = value.get("messages", [])

                for message in messages:

                    sender = message.get("from")
                    message_id = message.get("id")
                    message_type = message.get("type")

                    print(
                        f"=== MESSAGE === "
                        f"sender={sender}, "
                        f"type={message_type}",
                        flush=True
                    )

                    if not sender:
                        continue

                    # Mark incoming message as read
                    if message_id:
                        mark_as_read(message_id)

                    # TEXT MESSAGE
                    if message_type == "text":

                        user_text = (
                            message.get("text", {})
                            .get("body", "")
                            .strip()
                        )

                        print(
                            f"USER TEXT: {user_text}",
                            flush=True
                        )

                        # Simple automatic responses
                        text_lower = user_text.lower()

                        if text_lower in [
                            "hi",
                            "hello",
                            "hey",
                            "hii",
                            "habari",
                            "mambo"
                        ]:

                            reply = (
                                "Habari! 👋\n\n"
                                "Karibu WOLFE TZ 🤖🇹🇿\n"
                                "Nimepokea ujumbe wako.\n\n"
                                "Nikusaidie nini?"
                            )

                        elif "how are you" in text_lower:

                            reply = (
                                "Niko vizuri kabisa 😎🔥\n"
                                "Asante kwa kuuliza!\n\n"
                                "Ungependa nikusaidie nini?"
                            )

                        else:

                            reply = (
                                "Asante kwa ujumbe wako 🙏\n\n"
                                "WOLFE TZ nimeupokea ujumbe wako.\n"
                                "Tafadhali niambie unahitaji msaada gani."
                            )

                        send_message(sender, reply)

                    # Ignore unsupported message types
                    else:

                        print(
                            f"Unsupported message type: "
                            f"{message_type}",
                            flush=True
                        )

    except Exception as e:

        print(
            "WEBHOOK ERROR:",
            str(e),
            flush=True
        )

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":

    port = int(os.getenv("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
