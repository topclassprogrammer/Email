import imaplib
import smtplib
from email import message_from_string
from email.message import Message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from environs import Env


class Email:
    GMAIL_SMTP = "smtp.gmail.com"
    GMAIL_IMAP = "imap.gmail.com"

    def __init__(self):
        env = Env()
        env.read_env()
        self.login: str = env('login')
        self.password: str = env('password')
        self.subject: str = 'Subject'
        self.recipients: list[str] = ['vasya@email.com', 'petya@email.com']
        self.message: str = 'Message'
        self.header: Optional[str] = None

    def send_message(self):
        msg = MIMEMultipart()
        msg['From']: str = self.login
        msg['To']: str = ', '.join(self.recipients)
        msg['Subject']: str = self.subject
        msg.attach(MIMEText(self.message))
        with smtplib.SMTP(self.GMAIL_SMTP, 587) as conn:
            conn.ehlo()
            conn.starttls()
            conn.ehlo()
            conn.login(self.login, self.password)
            res: dict = conn.sendmail(self.login, self.recipients,
                                      msg.as_string())
            return res

    def receive_message(self):
        with imaplib.IMAP4_SSL(self.GMAIL_IMAP) as mail:
            mail.login(self.login, self.password)
            mail.list()
            mail.select("inbox")
            criterion: str = '(HEADER Subject "%s")' % self.header \
                if self.header else 'ALL'
            result, data = mail.uid('search', criterion)
            assert data[0], 'There are no letters with current header'
            latest_email_uid: str = data[0].split()[-1]
            result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email: bytes = data[0][1]
        email_message: Message = message_from_string(raw_email.decode())
        return email_message


if __name__ == '__main__':
    email = Email()
    email.send_message()
    email.receive_message()
