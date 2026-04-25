# 📘 Guía de Uso — Agente Dawnly-IA

> **Versión:** 1.1.0  
> **Modelo base:** `deepseek-coder:latest` vía Ollama  
> **Última actualización:** Abril 2025  
> **Proyecto:** `~/Development/dawnly-ia`

---

## ¿Qué es Dawnly-IA?

Dawnly-IA es un agente local que interpreta comandos en lenguaje natural y los ejecuta directamente en tu sistema. Puede crear archivos, moverlos y enviar correos con adjuntos usando tu cuenta de Gmail — todo desde la terminal, sin interfaces gráficas.

---

## 🗂 Sistema de Prefijos de Ruta

El agente usa prefijos para resolver rutas absolutas. **Siempre debes especificarlos.**

| Prefijo | Ruta absoluta equivalente | Cuándo usarlo |
|---|---|---|
| `/project/` | `~/Development/dawnly-ia/` | Archivos del proyecto |
| `/local/` | `~/` (home del usuario) | Documentos, descargas, etc. |
| *(sin prefijo)* | `~/Development/dawnly-ia/` | Igual que `/project/`, no recomendado |

---

## 1. Creación de Archivos

**Estructura del comando:**
```
Crea el archivo [PREFIJO]/[RUTA/NOMBRE.ext] con el texto '[CONTENIDO]'
```

**Ejemplos:**
```
Crea el archivo /project/src/utils.py con el texto '# Utilidades del sistema'
Crea el archivo /project/config/settings.json con el texto '{"debug": true}'
Crea el archivo /local/Documents/notas.txt con el texto 'Revisar logs mañana'
```

**Reglas importantes:**
- Siempre incluye la extensión del archivo (`.py`, `.txt`, `.json`, etc.)
- El agente crea automáticamente las subcarpetas si no existen
- Usa comillas simples `' '` para el contenido

**❌ Evitar:**
```
Crea el archivo gmail           → sin extensión, puede crear carpeta
Pon este código en el archivo   → verbo ambiguo, no activa la creación
Genera utils                    → sin ruta ni extensión
```

---

## 2. Movimiento y Renombrado de Archivos

**Estructura del comando:**
```
Mueve el archivo '[ORIGEN]' al destino '[DESTINO]'
```

**Ejemplos:**
```
Mueve el archivo '/home/zavaleta/Downloads/foto.jpg' a '/home/zavaleta/Pictures/foto.jpg'
Mueve el archivo '/project/src/viejo.py' al destino '/project/src/nuevo.py'
```

**Reglas importantes:**
- Usa rutas absolutas completas (con `/home/zavaleta/...`)
- Las comillas simples alrededor de las rutas ayudan al modelo a no confundirse
- El agente crea el directorio destino si no existe

**❌ Evitar:**
```
Mueve el main a src             → rutas relativas sin prefijo completo
Renombra utils                  → sin origen ni destino claros
```

---

## 3. Envío de Correos con Gmail

**Estructura del comando:**
```
Envía el archivo [PREFIJO]/[RUTA] al correo [EMAIL] con el asunto '[ASUNTO]'
```

**Ejemplos:**
```
Envía el archivo /project/src/main.py al correo 20230568@utsh.edu.mx con el asunto 'Copia de seguridad'
Envía el archivo /local/Documents/reporte.pdf al correo jefe@empresa.com con el asunto 'Reporte Abril'
```

**Datos requeridos mínimos:**
| Campo | Obligatorio | Ejemplo |
|---|---|---|
| Destinatario | ✅ Sí | `20230568@utsh.edu.mx` |
| Asunto | ✅ Sí | `'Prueba de Agente'` |
| Archivo adjunto | ✅ Sí | `/project/src/main.py` |
| Cuerpo del mensaje | ❌ Opcional | se genera automáticamente |

**Primera vez:** El agente abrirá el navegador para autenticarte con Google OAuth2. Después de autorizar, cierra la ventana y el correo se envía automáticamente. Las siguientes veces ya no pedirá autorización.

**❌ Evitar:**
```
Mándame el main                 → sin correo destino ni asunto
Envía algo a mi correo          → "algo" y "mi correo" son ambiguos
```

---

## 🛠 Errores Comunes y Soluciones

| Error | Causa | Solución |
|---|---|---|
| `❌ JSON inválido del modelo` | El modelo devolvió texto malformado | Reintenta el mismo comando, el modelo no es determinista al 100% |
| `❌ El archivo adjunto no existe` | La ruta del adjunto es incorrecta | Verifica que el archivo exista y usa la ruta completa |
| `❌ gmail_service.py no está disponible` | Falta el módulo de Gmail | Asegúrate de que `src/gmail_service.py` existe |
| `❌ Error: 'nombre'` | El modelo usó una clave distinta en el JSON | El agente intenta claves alternativas automáticamente; si falla, reintenta |
| `KeyboardInterrupt` al autenticar | Se canceló el flujo OAuth2 | Vuelve a ejecutar el comando y completa la autenticación en el navegador |

---

## ⚠️ Limitaciones Actuales

- **El modelo no tiene memoria:** cada comando es independiente, no recuerda conversaciones anteriores
- **JSON frágil:** `deepseek-coder` a veces devuelve comillas tipográficas (`"`) o comas finales; el agente las limpia automáticamente pero puede fallar en casos extremos
- **Sin confirmación:** el agente ejecuta las acciones directamente, no pide confirmación antes de crear o mover archivos
- **Un archivo adjunto por correo:** actualmente no soporta múltiples adjuntos en un mismo envío
- **Contenido largo:** para archivos con mucho código, es mejor crear el archivo manualmente y usar el agente solo para enviarlo

---

## 🧠 Buenas Prácticas

1. **Verbos de acción directos:** usa `Crea`, `Mueve`, `Envía` — evita `"pon"`, `"guarda"`, `"manda"`
2. **Siempre incluye extensión:** `.py`, `.txt`, `.json`, `.pdf`
3. **Comillas simples para contenido y asuntos:** evita que caracteres especiales rompan el JSON
4. **Rutas absolutas para mover:** no uses rutas relativas como `./archivo.py`
5. **Un comando a la vez:** el agente no procesa instrucciones encadenadas como `"Crea X y luego envíalo"`

---

## 🚀 Funciones Disponibles

| Función | Estado |
|---|---|
| Crear archivos (`/project/` y `/local/`) | ✅ Activo |
| Mover y renombrar archivos | ✅ Activo |
| Enviar correos con adjunto (Gmail OAuth2) | ✅ Activo |
| Leer contenido de archivos | 🔜 Próximamente |
| Listar estructura de carpetas | 🔜 Próximamente |
| Ejecutar scripts o comandos | 🔜 Próximamente |

---

*Dawnly-IA — Agente local construido con Python, Ollama y Gmail API*