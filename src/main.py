import os
import requests
import json
import shutil
import re

# Esta línea importará la funcionalidad de Gmail cuando ya tengas el archivo creado
try:
    from gmail_service import enviar_correo
except ImportError:
    enviar_correo = None

# --- CONFIGURACIÓN ---
OLLAMA_API = "http://localhost:11434/api/generate"
MODELO = "deepseek-coder:latest"
HOME = os.path.expanduser("~")
RUTA_PROYECTO = os.path.join(HOME, "Development/dawnly-ia")

def obtener_archivos_descargas():
    """Lee físicamente la carpeta de descargas del usuario."""
    ruta = os.path.join(HOME, "Downloads")
    try:
        archivos = os.listdir(ruta)
        return f"En Descargas tienes: {', '.join(archivos)}"
    except Exception as e:
        return f"Error: {e}"

def crear_archivo_local(nombre_con_prefijo, contenido):
    """
    Crea archivos usando prefijos /local/ o /project/. 
    Mantiene la estructura de carpetas exacta que pidas.
    """
    base_proyecto = RUTA_PROYECTO
    base_sistema = HOME
    
    # 1. Limpiamos el nombre para asegurar que sea una ruta relativa válida
    # Si el nombre viene con /project/, lo quitamos para unirlo con la base
    if nombre_con_prefijo.startswith("/project/"):
        ruta_relativa = nombre_con_prefijo.replace("/project/", "", 1)
        ruta_completa = os.path.join(base_proyecto, ruta_relativa)
    elif nombre_con_prefijo.startswith("/local/"):
        ruta_relativa = nombre_con_prefijo.replace("/local/", "", 1)
        ruta_completa = os.path.join(base_sistema, ruta_relativa)
    else:
        ruta_completa = os.path.join(base_proyecto, nombre_con_prefijo)

    try:
        # Esto crea todas las subcarpetas necesarias (ej: src/)
        os.makedirs(os.path.dirname(ruta_completa), exist_ok=True)
        
        with open(ruta_completa, "w", encoding="utf-8") as f:
            f.write(contenido)
        return f"✅ Archivo creado exactamente en: {ruta_completa}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def mover_archivo_local(origen, destino):
    """Mueve o renombra un archivo físico."""
    try:
        origen = origen.replace("'", "").replace('"', "").strip()
        destino = destino.replace("'", "").replace('"', "").strip()
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.move(origen, destino)
        return f"✅ Éxito: Movido a {destino}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def consultar_agente(mensaje_usuario):
    """Procesa la petición con un prompt reforzado para evitar errores de ruta."""
    
    es_creacion = any(p in mensaje_usuario.lower() for p in ["crea", "genera", "escribe"])
    es_movimiento = any(p in mensaje_usuario.lower() for p in ["mueve", "renombra"])
    es_envio = any(p in mensaje_usuario.lower() for p in ["envía", "manda", "correo"])

    if es_creacion:
        prompt = (
            "SISTEMA DE ARCHIVOS - MODO ESTRICTO\n"
            "Regla: Mantén la ruta y extensión EXACTA pedida por el usuario.\n"
            "Ejemplo: 'Crea /project/src/test.py'\n"
            "Respuesta: {\"nombre\": \"/project/src/test.py\", \"contenido\": \"...\"}\n\n"
            f"PETICIÓN: {mensaje_usuario}\nJSON:"
        )
    elif es_envio:
        prompt = (
            "TAREA: Extraer datos para enviar correo.\n"
            "Responde SOLO con JSON válido sin comentarios ni comas finales:\n"
            "{\"destinatario\": \"EMAIL\", \"asunto\": \"ASUNTO\", \"cuerpo\": \"CUERPO\", \"adjunto\": \"RUTA_ARCHIVO\"}\n"
            "IMPORTANTE: Si el usuario menciona un archivo, SIEMPRE incluye su ruta exacta en 'adjunto'.\n"
            f"PETICIÓN: {mensaje_usuario}\nJSON:"
        )
    elif es_movimiento:
        prompt = "TAREA: Mover archivo. Responde solo JSON: {\"origen\": \"...\", \"destino\": \"...\"}\n"
    else:
        info = obtener_archivos_descargas()
        prompt = f"CONTEXTO: {info}\nPREGUNTA: {mensaje_usuario}\nRespuesta breve:"

    payload = {
        "model": MODELO,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0}
    }

    try:
        response = requests.post(OLLAMA_API, json=payload)
        texto_res = response.json().get("response", "").strip()

        # DEBUG: ver qué devuelve el modelo exactamente
        print(f"🔍 DEBUG raw: {texto_res}")
        import re

        if any([es_creacion, es_movimiento, es_envio]) and "{" in texto_res:
            inicio, fin = texto_res.find("{"), texto_res.rfind("}") + 1
            json_str = texto_res[inicio:fin]

            # --- LIMPIEZA ROBUSTA DE JSON SUCIO ---
            # 1. Reemplaza comillas tipográficas curvas por comillas escapadas
            json_str = json_str.replace('\u201c', '\\"').replace('\u201d', '\\"')  # " "
            json_str = json_str.replace('\u2018', "\\'").replace('\u2019', "\\'")  # ' '
            # 2. Quita comas finales antes de } o ]
            json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
            # 3. Elimina comentarios tipo // ...
            json_str = re.sub(r'//.*', '', json_str)
            # --------------------------------------

            print(f"🔍 DEBUG limpio: {json_str}")

            try:
                datos = json.loads(json_str)
            except json.JSONDecodeError as je:
                return f"❌ JSON inválido del modelo: {je}\nRaw: {json_str}"

            if es_creacion:
                nombre = (
                    datos.get('nombre') or datos.get('archivo') or
                    datos.get('file') or datos.get('path') or
                    datos.get('ruta') or next(iter(datos.keys()), None)
                )
                contenido = (
                    datos.get('contenido') or datos.get('content') or
                    datos.get('codigo') or datos.get('code') or ""
                )
                if not nombre:
                    return "❌ Error: No se encontró la clave del nombre en la respuesta."
                return crear_archivo_local(nombre, contenido)

            if es_movimiento:
                return mover_archivo_local(datos.get('origen'), datos.get('destino'))

            if es_envio:
                if enviar_correo is None:
                    return "❌ gmail_service.py no está disponible."
                
                adjunto = datos.get('adjunto', '')
                print(f"🔍 DEBUG adjunto raw: '{adjunto}'")  # <-- agrega esto
                
                # Resolver ruta del adjunto
                if adjunto.startswith('/project/'):
                    adjunto = adjunto.replace('/project/', RUTA_PROYECTO + '/', 1)
                elif adjunto.startswith('/local/'):
                    adjunto = adjunto.replace('/local/', HOME + '/', 1)
                
                print(f"🔍 DEBUG adjunto resuelto: '{adjunto}'")  # <-- y esto
                
                # Verificar que el archivo exista
                if adjunto and not os.path.exists(adjunto):
                    return f"❌ El archivo adjunto no existe en: {adjunto}"
                
                return enviar_correo(
                    datos.get('destinatario', ''),
                    datos.get('asunto', ''),
                    datos.get('cuerpo', 'Enviado por el Agente'),
                    adjunto or None
                )

        return texto_res

    except Exception as e:
        return f"Error: {e}"

# --- BUCLE ---
print(f"--- Agente Local Activo ({MODELO}) ---")
while True:
    pregunta = input("\n📝 Tú: ")
    if pregunta.lower() in ["salir", "exit"]: break
    print(f"🤖 Agente: {consultar_agente(pregunta)}")