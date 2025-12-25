from twilio.rest import Client
from django.conf import settings

def send_whatsapp_message(message_text):
    sid = settings.TWILIO_SID
    token = settings.TWILIO_AUTH_TOKEN
    from_ = settings.TWILIO_WHATSAPP_FROM
    to = settings.TWILIO_WHATSAPP_TO

    if not (sid and token and from_ and to):
        print("Twilio credentials not configured; skipping WhatsApp.")
        return

    try:
        client = Client(sid, token)
        message = client.messages.create(body=message_text, from_=from_, to=to)
        print("WhatsApp sent, sid:", message.sid)
    except Exception as e:
        print("WhatsApp send failed:", e)
