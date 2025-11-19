import imaplib
import email
from email.header import decode_header
import logging
import os

def fetch_attachments(source_config):
    """
    Connects to an IMAP server, fetches unseen emails, and extracts attachments.
    
    Args:
        source_config (dict): Contains 'host', 'user', and 'password'.
        
    Returns:
        list: A list of dictionaries, each containing 'filename', 'content' (bytes), and 'metadata'.
    """
    host = source_config.get('host')
    user = source_config.get('user')
    password = source_config.get('password')

    if not all([host, user, password]):
        logging.error(f"Missing IMAP configuration for user {user}")
        return []

    attachments_found = []

    try:
        logging.info(f"Connecting to IMAP server {host} for user {user}...")
        
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(host)
        mail.login(user, password)
        
        # Select inbox
        mail.select("inbox")
        
        # Search for unseen emails
        status, messages = mail.search(None, "UNSEEN")
        
        if status != "OK":
            logging.warning("No messages found or error searching inbox.")
            return []

        email_ids = messages[0].split()
        logging.info(f"Found {len(email_ids)} new emails.")

        for email_id in email_ids:
            # Fetch the email body
            res, msg_data = mail.fetch(email_id, "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Decode subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    sender = msg.get("From")
                    logging.info(f"Processing email from: {sender}, Subject: {subject}")

                    # Iterate over email parts
                    for part in msg.walk():
                        if part.get_content_maintype() == "multipart":
                            continue
                        if part.get("Content-Disposition") is None:
                            continue

                        filename = part.get_filename()
                        if filename:
                            # Decode filename if necessary
                            filename_decoded, filename_encoding = decode_header(filename)[0]
                            if isinstance(filename_decoded, bytes):
                                filename = filename_decoded.decode(filename_encoding if filename_encoding else "utf-8")

                            # Filter by extension (Architecture requirement)
                            if not filename.lower().endswith(('.pdf', '.jpg', '.png', '.jpeg')):
                                logging.info(f"Skipping file with unsupported extension: {filename}")
                                continue

                            content = part.get_payload(decode=True)
                            if content:
                                attachments_found.append({
                                    "filename": filename,
                                    "content": content,
                                    "metadata": {
                                        "sender": sender,
                                        "subject": subject,
                                        "email_id": email_id.decode()
                                    }
                                })
                                logging.info(f"Found attachment: {filename}")

        mail.close()
        mail.logout()
        
    except Exception as e:
        logging.error(f"IMAP Error for {user}: {str(e)}")
    
    return attachments_found
