import imaplib
import email
import os

from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()

IMAP_SERVER = "imap.gmail.com"

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")


class EmailFetcher:

    def __init__(self):
        self.mail = None

    def connect(self):
        try:
            self.mail = imaplib.IMAP4_SSL(
                IMAP_SERVER,
                993,
                timeout=30
            )

            self.mail.login(EMAIL, PASSWORD)

            print("Connected successfully")

        except imaplib.IMAP4.abort as e:
            print(f"IMAP aborted connection: {e}")

        except Exception as e:
            print(f"Connection failed: {e}")

    def fetch_recent_emails(self, limit=10):
        self.mail.select("inbox")

        status, messages = self.mail.search(None, "ALL")

        email_ids = messages[0].split()
        latest_ids = email_ids[-limit:]

        results = []

        for e_id in latest_ids:
            _, msg_data = self.mail.fetch(e_id, "(RFC822)")

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    subject, encoding = decode_header(msg["Subject"])[0]

                    if isinstance(subject, bytes):
                        subject = subject.decode(
                            encoding if encoding else "utf-8",
                            errors="ignore"
                        )

                    sender = msg.get("From")
                    date = msg.get("Date")

                    body = ""

                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                try:
                                    body = part.get_payload(decode=True).decode(errors="ignore")
                                except:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode(errors="ignore")
                        except:
                            pass

                    results.append({
                        "uid": e_id.decode(),
                        "sender": sender,
                        "subject": subject,
                        "body": body,
                        "date": date
                    })

        return results


if __name__ == "__main__":
    fetcher = EmailFetcher()
    fetcher.connect()

    emails = fetcher.fetch_recent_emails()

    for mail in emails:
        print(mail["subject"])