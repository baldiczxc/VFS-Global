from email.mime.multipart import MIMEMultipart
import smtplib

from config import your_email, email_to


def send_mail(secret_key_gmail, city):
    sender_email = f'{your_email}'
    sender_password = f'{secret_key_gmail}'
    receiver_email = f'{email_to}'

    # Создание объекта сообщения
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = f'Даты есть у {city}!!!'

    # Отправка сообщения по SMTP
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
