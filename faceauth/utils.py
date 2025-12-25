import os
import smtplib
from email.message import EmailMessage
from django.conf import settings
from deepface import DeepFace


# ✅ FACE VERIFICATION FUNCTION (WAS MISSING)
def verify_against_db(live_image_path, threshold=1.10):

    if not os.path.exists(settings.AUTHORIZED_DB):
        os.makedirs(settings.AUTHORIZED_DB)

    persons = [
        p for p in os.listdir(settings.AUTHORIZED_DB)
        if os.path.isdir(os.path.join(settings.AUTHORIZED_DB, p))
    ]

    if not persons:
        return False, "No reference data", None

    for person in persons:
        folder = os.path.join(settings.AUTHORIZED_DB, person)
        for img in os.listdir(folder):
            auth_img = os.path.join(folder, img)
            try:
                result = DeepFace.verify(
                    img1_path=live_image_path,
                    img2_path=auth_img,
                    model_name="Facenet512",
                    detector_backend="opencv",
                    distance_metric="euclidean_l2",
                    enforce_detection=False
                )

                dist = result.get("distance")
                if result.get("verified") and dist is not None and dist < threshold:
                    return True, person, dist

            except Exception:
                continue

    return False, "Unknown", None


# ✅ EMAIL FUNCTION
def send_email(is_authorized, person_name, image_path):

    sender = settings.SMTP_EMAIL
    password = settings.SMTP_PASSWORD
    receiver = settings.SMTP_RECEIVER

    if not sender or not password or not receiver:
        print("❌ Email credentials not set")
        return

    msg = EmailMessage()

    if is_authorized:
        msg["Subject"] = f"✔ AUTHENTICATED PERSON: {person_name}"
        msg.set_content(f"{person_name} was authenticated successfully.")
    else:
        msg["Subject"] = "🚨 UNAUTHORIZED PERSON DETECTED!"
        msg.set_content("An unknown person tried to access the system.")

    msg["From"] = sender
    msg["To"] = receiver

    try:
        with open(image_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="image",
                subtype="jpeg",
                filename="capture.jpg"
            )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)

        print("✅ Email sent successfully")

    except Exception as e:
        print("❌ Email sending failed:", e)
