from google_auth_oauthlib.flow import InstalledAppFlow
import json

scopes = ['https://www.googleapis.com/auth/gmail.send']

def gerar_token():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', scopes=scopes)
    
    creds = flow.run_local_server(port=0)

    with open('token.json', 'w') as token_file:
        token_file.write(creds.to_json())
    print("Arquivo token.json gerado com sucesso.")

if __name__ == '__main__':
    gerar_token()
