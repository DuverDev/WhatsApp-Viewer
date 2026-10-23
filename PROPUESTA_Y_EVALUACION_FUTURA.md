# Propuesta de Evolución y Evaluación Técnica: WhatsApp Backup Viewer

Este documento analiza tres iniciativas clave para el futuro del proyecto **WhatsApp Backup Viewer**:
1. Implementación del botón nativo **"Abrir carpeta de chats"** desde la interfaz.
2. Expansión del motor de parseo a los **5 idiomas más populares** de WhatsApp a nivel global.
3. Evaluación exhaustiva de **viabilidad, costos y arquitectura** para publicar la aplicación en **iPhone (iOS)**.

---

## 1. Botón "Abrir carpeta de chats" desde la App

### 1.1. Objetivo
Brindar al usuario una forma inmediata y sin fricción de abrir la carpeta `chats/` en el Explorador de Archivos de Windows (o el gestor de archivos nativo de su sistema operativo) con un solo clic desde la barra lateral.

### 1.2. Implementación Técnica Propuesta

#### Backend (`server.py`)
Se agrega un endpoint específico que invoca el comando del sistema operativo para abrir la carpeta sin bloquear la interfaz:

```python
import os
import subprocess
import sys

@app.route("/api/open-chats", methods=["POST"])
def open_chats_directory():
    try:
        CHATS_DIR.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(str(CHATS_DIR))
        elif sys.platform == "darwin":  # macOS
            subprocess.Popen(["open", str(CHATS_DIR)])
        else:  # Linux
            subprocess.Popen(["xdg-open", str(CHATS_DIR)])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

#### Frontend (`templates/index.html`)
Se añade un botón con icono de carpeta en la sección de "Chats" (junto al botón de recargar `↻`):

```html
<h3>
  <span data-i18n="chatsTitle">Chats</span>
  <div style="margin-left:auto; display:flex; gap:4px;">
    <button class="btn-icon" onclick="openChatsFolder()" data-i18n-title="openChatsFolder" title="Abrir carpeta en el explorador">&#128194;</button>
    <button class="btn-icon" onclick="loadChats()" data-i18n-title="refreshChats" title="Actualizar lista">&#8635;</button>
  </div>
</h3>
```

```javascript
function openChatsFolder() {
  fetch('/api/open-chats', { method: 'POST' }).catch(function(e) {
    alert(t('errorOpeningFolder', 'No se pudo abrir la carpeta'));
  });
}
```

- **Esfuerzo estimado:** 30 a 45 minutos.
- **Riesgo técnico:** Mínimo (0%).

---

## 2. Soporte de los 5 Idiomas Más Populares en el Parser

### 2.1. Alcance
El objetivo es que el **motor de lectura de chats (`parser.py`)** entienda automáticamente las exportaciones de WhatsApp generadas en los dispositivos configurados en los 5 idiomas principales de la plataforma, sin importar qué idioma tenga seleccionado el usuario en la interfaz visual.

Los 5 idiomas con mayor volumen de usuarios en WhatsApp a nivel global son:
1. **Español (ES)** *(Ya implementado)*
2. **Inglés (EN)** *(Ya implementado)*
3. **Portugués (PT)** (Brasil y Portugal: más de 120M de usuarios)
4. **Francés (FR)** (Francia, África francófona, Canadá)
5. **Alemán (DE)** / **Italiano (IT)** (Europa central y del sur)

*(Nota: En mercados como India con Hindi, la inmensa mayoría de las exportaciones de teléfonos se configuran en inglés; no obstante, también se contemplan las cadenas en Hindi/Devanagari).*

---

### 2.2. Variaciones Críticas por Idioma en WhatsApp

| Idioma | Frase de Archivo Adjunto | Mensaje de Multimedia Omitido | Remitente Propio por Defecto | Particularidades de Fecha/Hora |
| :--- | :--- | :--- | :--- | :--- |
| **Español** | `(archivo adjunto)` o `<adjunto: ...>` | `<Multimedia omitido>` | `Tú` | `DD/MM/AAAA, HH:MM` o `a. m. / p. m.` |
| **Inglés** | `(file attached)` o `<attached: ...>` | `<Media omitted>` | `You` | `MM/DD/YY, H:MM PM` o `[MM/DD/YY, H:MM:SS PM]` |
| **Portugués** | `(arquivo anexado)` o `<anexado: ...>` | `<Arquivo de mídia oculto>` / `<Mídia omitida>` | `Você` | `DD/MM/AAAA HH:MM` (a veces sin coma) |
| **Francés** | `(fichier joint)` o `<pièce jointe : ...>` | `<Médias omis>` / `<Fichier omis>` | `Vous` | `DD/MM/YYYY à HH:MM` (usa ` à ` como separador) |
| **Alemán** | `(Datei angehängt)` o `<angehängt: ...>` | `<Medien weggelassen>` | `Du` | `DD.MM.YY, HH:MM` (usa puntos y a veces sufijo `Uhr`) |
| **Italiano** | `(file allegato)` o `<allegato: ...>` | `<Contenuti multimediali omessi>` | `Tu` | `DD/MM/YY, HH:MM` |

---

### 2.3. Cambios Necesarios en `parser.py` y `server.py`

1. **Patrones de adjuntos unificados (`_MEDIA_ATTACH_PATTERNS`):**
   ```python
   _MEDIA_ATTACH_PATTERNS = [
       re.compile(r"^(.+?)\s*\((?:archivo adjunto|file attached|arquivo anexado|fichier joint|datei angehängt|file allegato)\)$", re.IGNORECASE),
       re.compile(r"^<(?:\s*attached|\s*adjunto|\s*anexado|\s*pièce jointe|\s*angehängt|\s*allegato)\s*:\s*(.+?)>$", re.IGNORECASE),
   ]
   ```

2. **Detección de multimedia omitido (`_MEDIA_OMITTED`):**
   ```python
   _MEDIA_OMITTED = re.compile(
       r"^<.*(?:omitido|omitted|oculto|omis|weggelassen|omessi).*>$", re.IGNORECASE
   )
   ```

3. **Separador de fecha y hora para Francés y Alemán:**
   - Ampliar la expresión regular para admitir `[,\s]+|(?:\s+à\s+)` entre fecha y hora.
   - Permitir `\s*(?:Uhr)?` opcional al final de la hora en exportaciones en alemán.

4. **Identificación de usuario propio (`my_name` en `server.py`):**
   ```python
   SELF_SENDERS = {"Tú", "You", "Você", "Vous", "Du", "Tu"}
   my_name = next((s for s in senders if s in SELF_SENDERS), (senders[0] if senders else ""))
   ```

- **Complejidad:** **Baja**.
- **Impacto de Rendimiento:** **Nulo** (las expresiones regulares compiladas se ejecutan en microsegundos).
- **Tiempo estimado:** 1 a 2 días (incluyendo conjunto de pruebas sintéticas para cada idioma).

---

## 3. Evaluación Exhaustiva: Llevar la App a iPhone (iOS)

Llevar la aplicación a iOS representa un cambio de arquitectura de gran envergadura debido a las restricciones inherentes del ecosistema de Apple.

---

### 3.1. El Reto Técnico Fundamental: Incompatibilidad de la Arquitectura Actual
- **Estado Actual:** Python 3 + Flask + PyInstaller + `pywebview`.
- **Restricción de iOS / App Store:**
  - Apple **NO permite** distribuir un runtime estándar de Python que levante servidores Flask en segundo plano vía sockets locales (`127.0.0.1`) sin sandbox.
  - PyInstaller **no compila binarios para iOS** (solo Windows, macOS y Linux).
  - La App Store prohíbe ejecutables que no estén firmados y compilados para ARM64 utilizando los frameworks nativos de Apple (iOS SDK).

---

### 3.2. Rutas Tecnológicas de Adaptación a iOS

| Criterio | Opción A: Web App Local / PWA | Opción B: Híbrida (Capacitor / Ionic) | Opción C: Nativa 100% (Swift / SwiftUI) |
| :--- | :--- | :--- | :--- |
| **Descripción** | PWA que corre en Safari sin App Store | Se empaqueta la UI web existente en un contenedor nativo de iOS (WKWebView) | Se reescribe la interfaz y el parser en lenguaje Swift nativo |
| **Reutilización de código actual** | 70% (solo el frontend) | **85%** (se conserva todo el HTML/CSS/JS de `index.html`) | 0% (reescritura total) |
| **Parser** | Debe reescribirse en JavaScript/Web Worker | Parser portado a JavaScript o plugin nativo en Swift | Parser implementado en Swift |
| **Distribución** | Enlace web / Guardar en pantalla de inicio | **App Store oficial de Apple** | **App Store oficial de Apple** |
| **Manejo de archivos** | Muy limitado en Safari (subir zip cada vez) | Soporta *Share Sheet* y acceso a app *Archivos* | Acceso completo al sandbox de archivos e integración nativa |
| **Tiempo estimado** | 1 a 2 semanas | **2 a 3 semanas (Recomendada)** | 4 a 6 semanas |

> **Ruta Recomendada: Opción B (Capacitor + Frontend Vanilla)**  
> Permite mantener el diseño actual de WhatsApp Web de `index.html`, elimina por completo la necesidad de un servidor Flask en segundo plano, y utiliza la API de almacenamiento de Capacitor para descomprimir los archivos `.zip` exportados directamente en el sandbox del iPhone.

---

### 3.3. Cambios Arquitectónicos Necesarios para iOS

1. **Eliminar el Backend Flask:**
   - La API (`/api/chats`, `/api/chats/.../messages`) se reemplaza por un **módulo en JavaScript (o Swift)** que lee directamente del almacenamiento local del iPhone.
   - El parser (`parse_whatsapp_backup`) se convierte a JavaScript puro para ejecutarse en el cliente en un *Web Worker* (evitando congelar la pantalla con 60.000 mensajes).
2. **Sistema de Ingesta de Archivos en iOS:**
   - En Windows, el usuario simplemente arrastra carpetas a `chats/`.
   - En iOS **no existe una carpeta `chats/` accesible de forma libre**. El flujo en iPhone debe ser:
     1. El usuario va a WhatsApp -> *Exportar chat* -> *Compartir*.
     2. En el menú de compartir de iOS, selecciona **"WhatsApp Viewer"**.
     3. La app recibe el archivo `.zip` o `.txt`, lo descomprime en su sandbox privado y lo lista en pantalla automáticamente.
     4. Alternativamente: botón *"Importar desde Archivos"* mediante el selector de documentos de iOS (`UIDocumentPickerViewController`).

---

### 3.4. Costos Económicos y Requisitos de Apple

| Concepto | Costo | Frecuencia | Descripción |
| :--- | :--- | :--- | :--- |
| **Apple Developer Program** | **$99 USD** | Anual (Obligatorio) | Licencia indispensable para firmar y publicar en la App Store o distribuir betas en TestFlight. |
| **Hardware Mac (macOS)** | **$600 - $1,000 USD** *(o $0 si ya tienes una Mac)* | Pago único | Para compilar, firmar y enviar binarios de iOS se requiere una computadora Mac con Xcode. *(Alternativa en la nube: Mac virtual o GitHub Actions a ~$0.08/min).* |
| **Servidores / Backend** | **$0 USD** | - | La app permanece 100% offline y local en el dispositivo del usuario, sin costos de hosting. |
| **Dominio y Web de Privacidad** | **$10 - $15 USD** | Anual | Apple exige obligatoriamente una URL pública de Política de Privacidad (ej. `DMDevLabs.com/privacy`). |

---

### 3.5. Políticas de Aprobación de la App Store (Riesgos a Considerar)

1. **Propiedad Intelectual y Marca:**
   - Apple es estricta con el uso de marcas registradas. La app **no podrá llamarse simplemente "WhatsApp Viewer"** en la App Store ni usar el icono oficial de WhatsApp, o será rechazada de inmediato.
   - Nombres recomendados: *"Chat Backup Viewer"*, *"Backup Viewer for WA"*, o *"W-Viewer: Local Backup"*.
2. **Directriz 4.2 (Funcionalidad Mínima):**
   - La app debe tener un flujo de bienvenida claro si no hay ningún chat cargado para que el revisor de Apple no la rechace por falta de contenido inicial (incluir un chat de muestra precargado soluciona esto).
3. **Privacidad:**
   - Dado que la app es 100% offline, supera fácilmente la revisión de privacidad de Apple (declarando cero recopilación de datos en los *Privacy Nutrition Labels*).

---

## 4. Matriz Comparativa y Hoja de Ruta

| Funcionalidad | Complejidad | Costo Estimado | Tiempo de Desarrollo | Recomendación |
| :--- | :---: | :---: | :---: | :---: |
| **1. Botón "Abrir carpeta"** | Muy Baja | $0 | 1 hora | **Implementar de inmediato** en la versión de escritorio. |
| **2. Soporte 5 Idiomas en Parser** | Baja | $0 | 1 - 2 días | **Implementar a corto plazo**; universaliza el producto globalmente. |
| **3. Versión para iPhone (iOS)** | Alta | $99 USD/año (+ Mac) | 2 - 3 semanas | **Evaluar según demanda comercial**; requiere migración a Capacitor. |

---
*Documento elaborado para planificación técnica y toma de decisiones en el proyecto WhatsApp Backup Viewer.*

