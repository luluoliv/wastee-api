import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
import random
from .models import ConfirmationCode
from django.utils import timezone

def enviar_codigo_email(email_destinatario, codigo):
    try:
        assunto = 'Seu código de confirmação'
        mensagem = f'Seu código de confirmação é: {codigo}'
        email_remetente = settings.EMAIL_HOST_USER
        senha_remetente = settings.EMAIL_HOST_PASSWORD
        msg = MIMEMultipart()
        msg['From'] = email_remetente
        msg['To'] = email_destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(mensagem, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Inicia a conexão TLS
            server.login(email_remetente, senha_remetente)
            server.send_message(msg)  # Envia a mensagem

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

def gerar_codigo_confirmacao(user):
    codigo = random.randint(100000, 999999)
    confirmation_code = ConfirmationCode.objects.create(
        user=user,
        confirmation_code=codigo,
        is_used=False,
        expiration_time=timezone.now() + timezone.timedelta(minutes=10)
    )
    return codigo
