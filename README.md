# WhatsApp Backup Viewer (v1.2.1)

Visualizador local de chats exportados de WhatsApp. Gratuito, de codigo abierto y 100% offline.

Desarrollado por **DMDev Labs** — [dmdevlabs.com](https://dmdevlabs.com)

## Caracteristicas

- Visualizacion de mensajes con burbujas estilo WhatsApp (soporte bilingue ES/EN)
- Tema **Claro por defecto** y **Modo Oscuro** conmutables
- Soporte completo de multimedia: fotos, videos, audios, stickers y documentos (con tamano real en documentos y leyendas limpias sin etiquetas tecnicas)
- Galeria multimedia organizada por tipo
- Busqueda de texto con navegacion entre resultados (Ctrl+F)
- Filtros por persona y por rango de fechas
- Estadisticas del chat (mensajes totales, participante mas activo, periodo)
- Rendimiento optimizado para chats de 30,000+ mensajes
- Manual de usuario integrado con instrucciones paso a paso y avisos legales GPL-3.0 / marcas actualizados
- **100% local** — ningun dato sale de tu equipo

## Requisitos

### Usar el ejecutable (recomendado)
- Windows 10/11 (64-bit)
- No requiere instalacion

### Ejecutar desde el codigo fuente
- Python 3.10 o superior
- Dependencias: `flask`, `pywebview`

## Inicio rapido

### Opcion 1: Ejecutable portable
1. Descarga `WhatsApp Viewer.exe` desde [Releases](../../releases)
2. Coloca el ejecutable en una carpeta
3. Crea una carpeta `chats/` junto al ejecutable
4. Exporta tus chats desde WhatsApp y colocalos dentro de `chats/`
5. Ejecuta `WhatsApp Viewer.exe`

### Opcion 2: Desde el codigo fuente
```bash
git clone https://github.com/DuverDev/WhatsApp-Viewer.git
cd WhatsApp-Viewer
pip install -r requirements.txt
python app.py
```

## Estructura de carpetas

```
WhatsApp Viewer.exe  (o python app.py)
chats/
    Juan Perez/
        Chat de WhatsApp con Juan Perez.txt
        IMG-20240115-WA0001.jpg
        AUD-20240115-WA0003.opus
    Grupo Familia/
        Chat de WhatsApp con Grupo Familia.txt
        VID-20240220-WA0005.mp4
```

Cada chat va en su propia subcarpeta dentro de `chats/`, con el archivo `.txt` exportado y opcionalmente los archivos multimedia.

## Como exportar un chat de WhatsApp

### Android
1. Abre el chat → Menu (**⋮**) → **Mas** → **Exportar chat**
2. Elige **"Incluir archivos"** o **"Sin archivos"**
3. Guarda el archivo en tu PC

### iPhone
1. Abre el chat → Toca el nombre del contacto/grupo
2. Baja y toca **"Exportar chat"**
3. Elige con o sin multimedia → Selecciona destino

> La app incluye un **Manual** integrado con instrucciones detalladas para WhatsApp y WhatsApp Business.

## Compilar el ejecutable

```bash
# Generar icono
python gen_icon.py

# Compilar .exe (requiere PyInstaller)
build.bat
```

El ejecutable portable y su archivo de verificación SHA-256 se generan en `dist/WhatsApp Viewer.exe` y `dist/WhatsApp Viewer.exe.sha256`.

## Tecnologias

- **Backend:** Python, Flask
- **Frontend:** HTML/CSS/JS vanilla (SPA)
- **Ventana nativa:** pywebview
- **Empaquetado:** PyInstaller

## Privacidad

- No recopila datos de ningun tipo
- No requiere conexion a internet
- Todo el procesamiento es local
- Sin telemetria, sin cookies, sin cuentas
- El servidor local (`127.0.0.1`) solo atiende a la propia ventana de la app: rechaza peticiones de otros sitios web y de otros dominios

## Verificación de Seguridad (VirusTotal)

Cada [release](../../releases/latest) trae el SHA-256 del ejecutable (también en el archivo `.sha256`) y el enlace a su informe en VirusTotal.

> [!NOTE]
> **Sobre las 4/70 alertas heurísticas en VirusTotal (Falsos Positivos de PyInstaller):**
> El binario oficial compilado en GitHub Actions recibe 0 detecciones en 66 de 70 motores (incluidos **Microsoft Defender, Kaspersky, Bitdefender, ESET, Malwarebytes, Google y Avast**). Únicamente 4 motores basados en heurística agresiva o aprendizaje automático (*Bkav Pro*, *CrowdStrike Falcon 60%*, *SecureAge* y *Skyhigh SWG*) emiten una alerta genérica porque:
> 1. Está empaquetado como ejecutable único con **PyInstaller (`--onefile`) y compresión UPX**, cuyo *bootloader* descomprime Python/Flask/pywebview en `%TEMP%` al iniciar.
> 2. Es software libre gratuito compilado en la nube sin un certificado comercial de firma de código EV de pago.
> 3. Todo el código fuente está 100 % abierto y verificable en este repositorio; si prefieres no usar el `.exe`, puedes ejecutarlo directo con `python app.py`.

## Licencia y condiciones de uso

- Código bajo la [GNU General Public License v3.0](LICENSE).
- Se entrega «tal cual» (*as is*), sin garantías. Al usarlo aceptas las [condiciones de uso](TERMINOS.md), las mismas de [dmdevlabs.com/terminos](https://dmdevlabs.com/terminos).
- WhatsApp es una marca de WhatsApp LLC / Meta Platforms, Inc. Este proyecto independiente de DMDev Labs no está afiliado, patrocinado ni respaldado por Meta o WhatsApp.
- Contacto: [contacto@dmdevlabs.com](mailto:contacto@dmdevlabs.com).

---

© 2026 DMDev Labs · [dmdevlabs.com](https://dmdevlabs.com)
