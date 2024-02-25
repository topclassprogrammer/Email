import smtplib
import imaplib
from email import message_from_string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from environs import Env


class Email:
    GMAIL_SMTP = "smtp.gmail.com"
    GMAIL_IMAP = "imap.gmail.com"

    def __init__(self):
        env = Env()
        env.read_env()
        self.login = env('login')
        self.password = env('password')
        self.subject = 'Subject'
        self.recipients = ['vasya@email.com', 'petya@email.com']
        self.message = 'Message'
        self.header = None

    def send_message(self):
        msg = MIMEMultipart()
        msg['From'] = self.login
        msg['To'] = ', '.join(self.recipients)
        msg['Subject'] = self.subject
        msg.attach(MIMEText(self.message))
        with smtplib.SMTP(self.GMAIL_SMTP, 587) as conn:
            conn.ehlo()
            conn.starttls()
            conn.ehlo()
            conn.login(self.login, self.password)
            return conn.sendmail(self.login, self.recipients, msg.as_string())

    def receive_message(self):
        with imaplib.IMAP4_SSL(self.GMAIL_IMAP) as mail:
            mail.login(self.login, self.password)
            mail.list()
            mail.select("inbox")
            criterion = '(HEADER Subject "%s")' % self.header if self.header \
                else 'ALL'
            result, data = mail.uid('search', criterion)
            assert data[0], 'There are no letters with current header'
            latest_email_uid = data[0].split()[-1]
            result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = data[0][1]
        email_message = message_from_string(raw_email.decode())
        return email_message


if __name__ == '__main__':
    email = Email()
    email.send_message()
    email.receive_message()
