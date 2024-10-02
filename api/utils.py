from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
import random
from .models import ConfirmationCode
from django.utils import timezone

def enviar_codigo_email(email_destinatario, codigo):
    try:
        assunto = 'Seu código de confirmação'
        mensagem = f'Seu código de confirmação é: {codigo}'
        email_remetente = settings.EMAIL_HOST_USER

        send_mail(
            assunto,
            mensagem,
            email_remetente,
            [email_destinatario],
            fail_silently=False,
        )

    except BadHeaderError:
        print("Cabeçalho inválido.")
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
