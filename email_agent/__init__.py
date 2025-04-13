import base64

import imapclient
import pyzmail
import os
import anthropic
from dotenv import load_dotenv


load_dotenv(verbose=True)


EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")
IMAP_SERVER = os.environ.get("IMAP_SERVER")
SAVE_ATTACHMENTS_TO = os.environ.get("SAVE_ATTACHMENTS_TO")
SUBJECT_TO_SEARCH = os.environ.get("SUBJECT_TO_SEARCH")


def fetch_attachments():
    os.makedirs(SAVE_ATTACHMENTS_TO, exist_ok=True)

    with imapclient.IMAPClient(IMAP_SERVER, ssl=True) as client:
        client.login(EMAIL, PASSWORD)
        client.select_folder('INBOX')

        # Search unread emails
        messages = client.search(['SUBJECT', SUBJECT_TO_SEARCH])

        print(f'Found {len(messages)} unread messages.')

        for uid in messages:
            raw_message = client.fetch([uid], ['BODY[]', 'FLAGS'])
            message = pyzmail.PyzMessage.factory(raw_message[uid][b'BODY[]'])

            print(f"From: {message.get_addresses('from')}")
            print(f"Subject: {message.get_subject()}")

            if message.mailparts:
                for part in message.mailparts:
                    if part.filename:
                        filepath = os.path.join(SAVE_ATTACHMENTS_TO, part.filename)
                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload())
                        print(f"Saved attachment: {filepath}")
                        extract_info_from_email(filepath)

def extract_info_from_email(filepath: str):
    client = anthropic.Anthropic()
    with open(filepath, 'rb') as f:
        raw_data = f.read()
        pdf_data = base64.standard_b64encode(raw_data).decode("utf-8")

    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data
                        }
                    },
                    {
                        "type": "text",
                        "text": "What are the key findings in this document?"
                    }
                ]
            }
        ],
    )

    print(message.content)
    return message.content


if __name__ == '__main__':
    fetch_attachments()