import imaplib
from email import message_from_bytes
from email.header import decode_header
from email.utils import parsedate_to_datetime


class GmailFetcher:
    def __init__(self, email_address, email_password):
        self.email_address = email_address
        self.email_password = email_password
        self.connection = None

    def connect(self):
        domain = self.email_address.rsplit("@", 1)[-1].lower()
        host = "imap.gmail.com" if domain == "gmail.com" else f"imap.{domain}"
        self.connection = imaplib.IMAP4_SSL(host)
        self.connection.login(self.email_address, self.email_password)
        self.connection.select("INBOX")
        return True

    @staticmethod
    def _decode_header(value):
        parts = []
        for text, encoding in decode_header(value or ""):
            parts.append(text.decode(encoding or "utf-8", errors="ignore") if isinstance(text, bytes) else text)
        return "".join(parts)

    @staticmethod
    def _body(message):
        parts = message.walk() if message.is_multipart() else [message]
        for part in parts:
            if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                payload = part.get_payload(decode=True) or b""
                return payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
        return ""

    def fetch_recent_emails(self, limit=10):
        if not self.connection:
            return []
        _, data = self.connection.search(None, "ALL")
        message_ids = data[0].split()[-limit:]
        results = []
        for message_id in reversed(message_ids):
            _, message_data = self.connection.fetch(message_id, "(RFC822)")
            raw_message = next((part[1] for part in message_data if isinstance(part, tuple)), None)
            if not raw_message:
                continue
            message = message_from_bytes(raw_message)
            received_at = message.get("Date")
            try:
                received_at = parsedate_to_datetime(received_at).isoformat()
            except (TypeError, ValueError):
                pass
            results.append(
                {
                    "uid": message_id.decode(),
                    "receiver": self._decode_header(message.get("To")),
                    "sender": self._decode_header(message.get("From")),
                    "subject": self._decode_header(message.get("Subject")) or "(No subject)",
                    "body": self._body(message),
                    "date": received_at,
                }
            )
        return results

    def close(self):
        if self.connection:
            try:
                self.connection.close()
            finally:
                self.connection.logout()
