import os
from django.apps import AppConfig
from django.conf import settings

class YourAppConfig(AppConfig):
    name = 'api'

    def ready(self):
        # Caminho do diretório de mídia
        media_root = os.path.join(settings.MEDIA_ROOT, 'seller_documents', 'rg')
        selfie_root = os.path.join(settings.MEDIA_ROOT, 'seller_documents', 'selfie')
        
        # Criar diretórios se não existirem
        os.makedirs(media_root, exist_ok=True)
        os.makedirs(selfie_root, exist_ok=True)
