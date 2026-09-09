import os
import requests
from flask import Flask, request

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "1385178644668054")

GRAPH_URL = f"https://graph.facebook.com/v26.0/{PHONE_NUMBER_ID}/messages"


@app.route("/", methods=["GET"])
def home():
    return "WOLFE TZ WhatsApp Bot is LIVE 🤖", 200


def whatsapp_request(payload):
    if not ACCESS_TOKEN:
        print("ERROR: ACCESS_TOKEN is missing", flush=True)
        return None

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            GRAPH_URL,
            headers=headers,
            json=payload,
            timeout=20,
        )

        print(
            "WhatsApp response:",
            response.status_code,
            response.text,
            flush=True,
        )

        return response

    except Exception as e:
        print("WhatsApp request error:", str(e), flush=True)
        return None


def send_typing(recipient, message_id):
    """
    Show typing indicator while processing the incoming message.
    If Meta rejects it, the bot continues normally.
    """

    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
        "typing_indicator": {
            "type": "text"
        },
    }

    response = whatsapp_request(payload)

    if response is not None:
        print(
            "Typing/read status:",
            response.status_code,
            flush=True,
        )


def send_message(recipient, text):
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {
            "body": text,
        },
    }

    return whatsapp_request(payload)


def create_reply(user_text):
    text = user_text.lower().strip()

    if text in ["hi", "hii", "hello", "hey"]:
        return (
            "Habari! 👋\n\n"
            "Karibu WOLFE TZ 🤖🇹🇿\n"
            "Nimepokea ujumbe wako.\n\n"
            "Nikusaidie nini?"
        )

    if text in ["habari", "mambo", "vipi"]:
        return (
            "Poa sana 😎🔥\n\n"
            "Karibu WOLFE TZ.\n"
            "Ungependa nikusaidie nini?"
        )

    if "how are you" in text:
        return (
            "Niko vizuri kabisa 😎🔥\n"
            "Asante kwa kuuliza!\n\n"
            "Ungependa nikusaidie nini?"
        )

    if "help" in text or "msaada" in text:
        return (
            "Nipo hapa kukusaidia 🤖\n\n"
            "Niambie tu unachohitaji."
        )

    return (
        "Asante kwa ujumbe wako 🙏\n\n"
        "WOLFE TZ nimeupokea ujumbe wako.\n"
        "Niambie unahitaji msaada gani."
    )


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
                    message_id = message.get("id")
                    message_type = message.get("type")

                    print(
                        f"=== MESSAGE === "
                        f"sender={sender}, "
                        f"type={message_type}",
                        flush=True,
                    )

                    if not sender:
                        continue

                    if message_type != "text":
                        print(
                            f"Unsupported message type: {message_type}",
                            flush=True,
                        )
                        continue

                    user_text = (
                        message.get("text", {})
                        .get("body", "")
                        .strip()
                    )

                    print(
                        f"USER TEXT: {user_text}",
                        flush=True,
                    )

                    # Try typing/read indicator.
                    # Failure here must NOT stop the bot.
                    if message_id:
                        try:
                            send_typing(sender, message_id)
                        except Exception as e:
                            print(
                                "Typing indicator failed:",
                                str(e),
                                flush=True,
                            )

                    reply = create_reply(user_text)

                    send_message(sender, reply)

    except Exception as e:

        print(
            "WEBHOOK ERROR:",
            str(e),
            flush=True,
        )

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":

    port = int(os.getenv("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port,
    )
