import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

def send_email(to: str, subject: str, content: str):
    with smtplib.SMTP(os.getenv('MAIL_HOST'), os.getenv('MAIL_PORT')) as server:
        server.starttls()
        server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
        msg = EmailMessage()
        msg['From'] = formataddr((os.getenv('MAIL_FROM_NAME'), os.getenv('MAIL_FROM_ADDRESS')))
        msg['To'] = to
        msg['Subject'] = subject
        msg.set_content(content)
        server.send_message(msg)
        server.quit()