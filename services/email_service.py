import os
import aiosmtplib
from email.message import EmailMessage
from email.utils import formataddr
import ssl

async def send_email(to: str, subject: str, content: str):
    context = ssl.create_default_context()
    smtp = aiosmtplib.SMTP(hostname=os.getenv('MAIL_HOST'), port=os.getenv('MAIL_PORT'), start_tls=False, use_tls=False)
    await smtp.connect()
    await smtp.starttls(tls_context=context)
    await smtp.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
    msg = EmailMessage()
    msg['From'] = formataddr((os.getenv('MAIL_FROM_NAME'), os.getenv('MAIL_FROM_ADDRESS')))
    msg['To'] = to
    msg['Subject'] = subject
    msg.set_content(content)
    await smtp.send_message(msg)
    await smtp.quit()