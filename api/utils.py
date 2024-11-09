import random
from api.models import ConfirmationCode

from django.utils import timezone

import logging
logger = logging.getLogger(__name__)

import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def enviar_email_oauth(email_destinatario, codigo):
    try:
        credentials = Credentials.from_authorized_user_file('token.json', scopes=[
            'https://www.googleapis.com/auth/gmail.send'
        ])
        

        assunto = 'Seu código de confirmação'
        mensagem = f'Seu código de confirmação é: {codigo}'

        msg = MIMEMultipart()
        msg['From'] = os.getenv('EMAIL_HOST_USER')
        msg['To'] = email_destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(mensagem, 'plain'))

        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        
        service = build('gmail', 'v1', credentials=credentials)
        message = {'raw': raw_message}

        service.users().messages().send(userId='me', body=message).execute()
        print("Email enviado com sucesso.")

    except Exception as e:
        logger.error(f"Erro ao enviar o e-mail: {e}")
        if 'invalid_grant' in str(e):
            print("Token expirado ou inválido. Verifique o refresh_token e tente novamente.")
        if not os.path.exists('token.json'):
            logger.error("Arquivo token.json não encontrado.")
        return


def gerar_codigo_confirmacao(user):
    codigo = random.randint(100000, 999999)
    expiration_time = timezone.now() + timezone.timedelta(minutes=10)
    
    ConfirmationCode.objects.create(
        user=user,
        confirmation_code=codigo,
        is_used=False,
        expiration_time=expiration_time
    )
    
    return codigo

