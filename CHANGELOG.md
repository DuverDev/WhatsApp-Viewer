# Cambios / Changelog

## 1.2.3 — 2026-11-19

### Seguridad
- **Adjuntos del chat aislados:** un documento `.html` o `.svg` recibido por WhatsApp podía ejecutar JavaScript al abrirlo en el visor y leer todos los chats. Ahora solo se muestran dentro de la app las imágenes, los videos, los audios y los PDF; lo demás se descarga como archivo, y ningún adjunto puede ejecutar código (`Content-Security-Policy: sandbox`, `X-Content-Type-Options: nosniff`). Con 2 pruebas nuevas.

## 1.2.2 — 2026-11-18

### Compilación
- PyInstaller 6.22.3 se compila en GitHub Actions con su propio arranque (*bootloader*) en vez del precompilado del paquete, que comparten muchos programas y marcan algunos antivirus por IA (falsos positivos como el de SentinelOne en la versión anterior).
- Sin compresión UPX, que también dispara alertas heurísticas.
- Sin cambios en el funcionamiento de la app.

## 1.2.1 — 2026-11-18

### Seguridad
- **Servidor local blindado:** la API en `127.0.0.1` solo atiende a la propia ventana de la app. Antes, una página web abierta en el navegador podía usar DNS rebinding contra el puerto fijo 5000 y leer los chats y archivos multimedia abiertos en el visor. Con 5 pruebas nuevas.

### Legal y marca
- Términos de uso iguales a los de [dmdevlabs.com/terminos](https://dmdevlabs.com/terminos), en español e inglés; también en `TERMINOS.md`.
- Marca unificada como **DMDev Labs** (interfaz, datos del `.exe` y documentación).

## 1.2.0 — 2026-11-14

### Interfaz, multimedia y legal
- **Tema Claro activado por defecto** (con conmutador rápido a Modo Oscuro).
- **Leyendas limpias en multimedia (`_clean_media_caption`):** se eliminan automáticamente las etiquetas técnicas `(archivo adjunto)` / `(file attached)` cuando acompañan imágenes, videos o documentos.
- **Metadatos reales en documentos (`_format_doc_size`):** las tarjetas de documentos muestran el tamaño real del archivo cuando está disponible en la carpeta del chat.
- **Avisos legales y de marcas actualizados:** términos bilingües ES/EN con licencia GPL-3.0, exención de responsabilidad («AS IS») y aclaración de no afiliación con WhatsApp LLC / Meta Platforms, Inc.

### Compilación y distribución
- Eliminación de certificados autofirmados locales (`create_cert.ps1` / `Set-AuthenticodeSignature`).
- Compilación automatizada desde GitHub Actions (`windows-latest`) con verificación SHA-256 (`.sha256`) y ejecución de pruebas unitarias (`pytest`).

### Verificación de seguridad (VirusTotal)
- **Hash oficial `WhatsApp.Viewer.exe` (SHA-256):** `922c12e3b0dddb0abbf43415f6baf21aaaadf4d7856d3dc21c87e6ac44f81c81`
- **Informe en VirusTotal:** https://www.virustotal.com/gui/file/922c12e3b0dddb0abbf43415f6baf21aaaadf4d7856d3dc21c87e6ac44f81c81
- **Falsos positivos heurísticos (4/70 motores frente a 66/70 limpios):** motores heurísticos/ML (*Bkav Pro*, *CrowdStrike Falcon 60%*, *SecureAge*, *Skyhigh SWG*) pueden alertar por el *bootloader* autoextraíble de **PyInstaller (`--onefile`)**, la compresión UPX y la ausencia de firma comercial EV de pago, mientras los antivirus principales (Microsoft Defender, Kaspersky, Bitdefender, ESET, Malwarebytes, Google, Avast) lo reportan limpio. El código es 100 % público y auditable (`python app.py`).

## 1.1.0 — 2026-10-23

- Soporte universal para chats exportados de WhatsApp en inglés (Android/iOS) e interfaz bilingüe ES/EN.

## 1.0.0 — 2026-10-22

- Lanzamiento inicial de WhatsApp Backup Viewer.
