import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import re
# Definimos los permisos necesarios (Alcances/Scopes)
# En este caso, solo permiso para enviar correos.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def obtener_servicio_gmail():
    """
    Gestiona la autenticación OAuth2.
    Lee 'credentials.json' y genera 'token.json' para sesiones futuras.
    """
    creds = None
    # El archivo token.json almacena los permisos del usuario
    token_path = 'config/token.json'
    # El archivo credentials.json es el que descargaste de Google Cloud
    creds_path = 'config/credentials.json'

    # 1. Intentar cargar credenciales existentes
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # 2. Si no hay credenciales válidas, iniciar el flujo de inicio de sesión
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"No se encontró el archivo de credenciales en {creds_path}")
            
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guardar las credenciales para la próxima vez
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    # Retornar el objeto de servicio de la API de Gmail
    return build('gmail', 'v1', credentials=creds)
def enviar_correo(destinatario, asunto, cuerpo, ruta_adjunto=None):
    """
    Crea y envía un mensaje de correo electrónico.
    """
    try:
        servicio = obtener_servicio_gmail()
        
        # Crear mensaje
        if ruta_adjunto and os.path.exists(ruta_adjunto):
            mensaje = MIMEMultipart()
            mensaje['to'] = destinatario
            mensaje['subject'] = asunto
            mensaje.attach(MIMEText(cuerpo, 'plain'))
            
            # Adjuntar archivo
            with open(ruta_adjunto, 'rb') as f:
                parte = MIMEBase('application', 'octet-stream')
                parte.set_payload(f.read())
                encoders.encode_base64(parte)
                nombre_archivo = os.path.basename(ruta_adjunto)
                parte.add_header('Content-Disposition', f'attachment; filename={nombre_archivo}')
                mensaje.attach(parte)
        else:
            mensaje = MIMEText(cuerpo, 'plain')
            mensaje['to'] = destinatario
            mensaje['subject'] = asunto

        # Codificar y enviar
        raw = base64.urlsafe_b64encode(mensaje.as_bytes()).decode()
        servicio.users().messages().send(userId='me', body={'raw': raw}).execute()
        return f"✅ Correo enviado a {destinatario}"
    
    except Exception as e:
        return f"❌ Error al enviar correo: {str(e)}"