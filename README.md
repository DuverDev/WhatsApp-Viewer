# WhatsApp Backup Viewer

Visualizador local de chats exportados de WhatsApp. Gratuito, de codigo abierto y 100% offline.

Desarrollado por **DMDevLabs** — [DMDevLabs.com](https://DMDevLabs.com)

## Caracteristicas

- Visualizacion de mensajes con burbujas estilo WhatsApp
- Soporte completo de multimedia: fotos, videos, audios, stickers y documentos
- Galeria multimedia organizada por tipo
- Busqueda de texto con navegacion entre resultados (Ctrl+F)
- Filtros por persona y por rango de fechas
- Estadisticas del chat (mensajes totales, participante mas activo, periodo)
- Modo claro y oscuro
- Rendimiento optimizado para chats de 30,000+ mensajes
- Manual de usuario integrado con instrucciones paso a paso
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

El ejecutable firmado se genera en `dist/WhatsApp Viewer.exe`.

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

## Licencia

Este proyecto esta licenciado bajo la [GNU General Public License v3.0](LICENSE).

## Disclaimer

WhatsApp es una marca registrada de Meta Platforms, Inc. Este proyecto no esta afiliado, patrocinado ni respaldado por Meta o WhatsApp.
