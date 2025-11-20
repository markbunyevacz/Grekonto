import unittest
from unittest.mock import MagicMock, patch
from shared import imap_client

class TestIMAPClient(unittest.TestCase):

    @patch('shared.imap_client.imaplib.IMAP4_SSL')
    def test_fetch_attachments_success(self, mock_imap_ssl):
        # Setup
        mock_mail = MagicMock()
        mock_imap_ssl.return_value = mock_mail
        
        # Mock login and select
        mock_mail.login.return_value = ('OK', [b'Logged in'])
        mock_mail.select.return_value = ('OK', [b'1'])
        
        # Mock search
        mock_mail.search.return_value = ('OK', [b'1'])
        
        # Mock fetch
        # Create a dummy email with attachment
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders

        msg = MIMEMultipart()
        msg['From'] = 'sender@example.com'
        msg['Subject'] = 'Invoice'
        
        # Add body
        msg.attach(MIMEText('Please find attached.', 'plain'))
        
        # Add attachment
        filename = "invoice.pdf"
        attachment = MIMEBase('application', 'pdf')
        attachment.set_payload(b'%PDF-1.4 dummy content')
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f'attachment; filename={filename}')
        msg.attach(attachment)
        
        raw_email = msg.as_bytes()
        mock_mail.fetch.return_value = ('OK', [(b'1 (RFC822 {100}', raw_email), b')'])

        source_config = {
            'host': 'imap.example.com',
            'user': 'user@example.com',
            'password': 'password'
        }

        # Execute
        attachments = imap_client.fetch_attachments(source_config)

        # Verify
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0]['filename'], 'invoice.pdf')
        self.assertEqual(attachments[0]['metadata']['sender'], 'sender@example.com')
        self.assertEqual(attachments[0]['metadata']['subject'], 'Invoice')

    @patch('shared.imap_client.imaplib.IMAP4_SSL')
    def test_fetch_attachments_no_emails(self, mock_imap_ssl):
        # Setup
        mock_mail = MagicMock()
        mock_imap_ssl.return_value = mock_mail
        mock_mail.search.return_value = ('OK', [b'']) # No emails

        source_config = {
            'host': 'imap.example.com',
            'user': 'user@example.com',
            'password': 'password'
        }

        # Execute
        attachments = imap_client.fetch_attachments(source_config)

        # Verify
        self.assertEqual(len(attachments), 0)

    def test_fetch_attachments_missing_config(self):
        # Setup
        source_config = {
            'host': 'imap.example.com',
            # Missing user and password
        }

        # Execute
        attachments = imap_client.fetch_attachments(source_config)

        # Verify
        self.assertEqual(len(attachments), 0)

if __name__ == '__main__':
    unittest.main()
