"""
mail_client.py — IMAP Connection & Email Parsing
=================================================
Handles everything IMAP-related:
  * Resolving the correct IMAP host from the email domain
  * Connecting with SSL and fetching ALL UNSEEN messages via BODY.PEEK[]
    (the PEEK flag ensures messages remain unread in the user's mailbox)
  * Decoding MIME headers and multipart message bodies
  * Stripping HTML to clean plain text
"""

import imaplib
import email
import html
import re
from email.header import decode_header, make_header

from classifier import classify_emotion


# ──────────────────────────────────────────────────────────────────────────────
# IMAP HOST RESOLUTION
# ──────────────────────────────────────────────────────────────────────────────

def resolve_imap_server(email_address: str) -> str:
    """Return the correct IMAP host for the given email address."""
    addr = email_address.strip().lower()
    if addr.endswith("@gmail.com"):
        return "imap.gmail.com"
    if any(addr.endswith(d) for d in ("@outlook.com", "@hotmail.com", "@live.com")):
        return "imap-mail.outlook.com"
    if addr.endswith("@yahoo.com"):
        return "imap.mail.yahoo.com"
    # Generic fallback — try imap.<domain>
    try:
        domain = addr.split("@", 1)[1]
        return f"imap.{domain}"
    except IndexError:
        return "imap.gmail.com"


# ──────────────────────────────────────────────────────────────────────────────
# TEXT UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def strip_html(raw: str) -> str:
    """Remove HTML tags and decode entities, returning readable plain text."""
    raw = re.sub(r"<style[^>]*>.*?</style>",  " ", raw, flags=re.DOTALL | re.IGNORECASE)
    raw = re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=re.DOTALL | re.IGNORECASE)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    raw = re.sub(r"[ \t]{2,}", " ", raw)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()


def decode_mime_words(s: str) -> str:
    """Safely decode MIME-encoded header values (e.g. =?UTF-8?B?...?=)."""
    if not s:
        return ""
    try:
        return str(make_header(decode_header(s)))
    except Exception:
        return s


# ──────────────────────────────────────────────────────────────────────────────
# MIME BODY EXTRACTION
# ──────────────────────────────────────────────────────────────────────────────

def extract_body(msg: email.message.Message) -> str:
    """
    Walk the MIME tree and return the best plain-text representation.

    Priority: text/plain > HTML-stripped text/html > '(No readable content)'
    Attachment parts are skipped.
    """
    plain_parts: list[str] = []
    html_parts:  list[str] = []

    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdisp = str(part.get("Content-Disposition", ""))
            if "attachment" in cdisp:
                continue
            charset = part.get_content_charset() or "utf-8"
            try:
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                text = payload.decode(charset, errors="replace")
            except Exception:
                continue

            if ctype == "text/plain":
                plain_parts.append(text)
            elif ctype == "text/html":
                html_parts.append(strip_html(text))
    else:
        charset = msg.get_content_charset() or "utf-8"
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                text = payload.decode(charset, errors="replace")
                if msg.get_content_type() == "text/html":
                    html_parts.append(strip_html(text))
                else:
                    plain_parts.append(text)
        except Exception:
            pass

    if plain_parts:
        return "\n".join(plain_parts).strip()
    if html_parts:
        return "\n".join(html_parts).strip()
    return "(No readable content)"


# ──────────────────────────────────────────────────────────────────────────────
# MAIN FETCH & SYNC FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def fetch_and_analyze(
    email_address: str,
    password: str,
    auto_mark_read: bool = False,
) -> list[dict]:
    """
    Connect to the IMAP server, fetch ALL UNSEEN messages using IMAP UIDs.
    If auto_mark_read is True, messages are marked as \\Seen in the mailbox
    (Gmail/Outlook/Yahoo) so they won't reappear on subsequent fetches.
    If auto_mark_read is False, messages remain unread until manually marked.

    Each dict contains:
        uid, subject, sender, date, body, emotion, polarity, subjectivity, is_read
    """
    imap_host = resolve_imap_server(email_address)
    results: list[dict] = []

    with imaplib.IMAP4_SSL(imap_host) as mail:
        mail.login(email_address, password)
        # If auto_mark_read is True, we must open with readonly=False so flags can be set
        mail.select("INBOX", readonly=not auto_mark_read)

        status, data = mail.uid("search", None, "UNSEEN")
        if status != "OK" or not data or not data[0]:
            return results

        uid_list = data[0].split()
        if not uid_list:
            return results

        fetched_uids: list[str] = []

        for uid_bytes in uid_list:
            uid_str = uid_bytes.decode("utf-8", errors="replace")
            try:
                status, msg_data = mail.uid("fetch", uid_bytes, "(BODY.PEEK[])")
                if status != "OK" or not msg_data:
                    continue

                raw_email = None
                for part in msg_data:
                    if isinstance(part, tuple):
                        raw_email = part[1]
                        break
                if raw_email is None:
                    continue

                msg     = email.message_from_bytes(raw_email)
                subject = decode_mime_words(msg.get("Subject", "(No Subject)"))
                sender  = decode_mime_words(msg.get("From", "Unknown"))
                date    = msg.get("Date", "")
                body    = extract_body(msg)

                emotion, polarity, subjectivity = classify_emotion(body)

                results.append({
                    "uid":          uid_str,
                    "subject":      subject,
                    "sender":       sender,
                    "date":         date,
                    "body":         body,
                    "emotion":      emotion,
                    "polarity":     round(polarity, 3),
                    "subjectivity": round(subjectivity, 3),
                    "is_read":      auto_mark_read,
                })
                fetched_uids.append(uid_str)

            except Exception as exc:
                results.append({
                    "uid":          uid_str,
                    "subject":      "(Error parsing this message)",
                    "sender":       "N/A",
                    "date":         "",
                    "body":         f"Could not parse message: {exc}",
                    "emotion":      "Normal",
                    "polarity":     0.0,
                    "subjectivity": 0.0,
                    "is_read":      False,
                })

        # If auto_mark_read is active, mark all fetched UIDs as Seen in the mailbox
        if auto_mark_read and fetched_uids:
            try:
                uids_csv = ",".join(fetched_uids)
                mail.uid("store", uids_csv, "+FLAGS", "(\\Seen)")
            except Exception:
                pass

    return results


def mark_as_read(email_address: str, password: str, uid: str) -> bool:
    """
    Mark a single email as \\Seen (Read) in the user's remote mailbox using its IMAP UID.
    """
    if not uid:
        return False
    imap_host = resolve_imap_server(email_address)
    with imaplib.IMAP4_SSL(imap_host) as mail:
        mail.login(email_address, password)
        mail.select("INBOX", readonly=False)
        mail.uid("store", str(uid), "+FLAGS", "(\\Seen)")
        mail.logout()
    return True


def mark_multiple_as_read(email_address: str, password: str, uids: list[str]) -> bool:
    """
    Mark a list of emails as \\Seen (Read) in the user's remote mailbox in one batch.
    """
    valid_uids = [str(u).strip() for u in uids if str(u).strip()]
    if not valid_uids:
        return True
    imap_host = resolve_imap_server(email_address)
    with imaplib.IMAP4_SSL(imap_host) as mail:
        mail.login(email_address, password)
        mail.select("INBOX", readonly=False)
        uids_csv = ",".join(valid_uids)
        mail.uid("store", uids_csv, "+FLAGS", "(\\Seen)")
        mail.logout()
    return True
