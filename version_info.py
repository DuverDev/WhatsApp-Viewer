"""Generate version_info.txt for PyInstaller --version-file."""

VERSION = (1, 0, 0, 0)

info = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={VERSION},
    prodvers={VERSION},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          '040904B0',
          [
            StringStruct('CompanyName', 'DMDevLabs'),
            StringStruct('FileDescription', 'WhatsApp Backup Viewer - Visualizador de chats exportados'),
            StringStruct('FileVersion', '{VERSION[0]}.{VERSION[1]}.{VERSION[2]}.{VERSION[3]}'),
            StringStruct('InternalName', 'WhatsApp Viewer'),
            StringStruct('LegalCopyright', 'Copyright (C) 2024 DMDevLabs - GPL-3.0 License'),
            StringStruct('OriginalFilename', 'WhatsApp Viewer.exe'),
            StringStruct('ProductName', 'WhatsApp Backup Viewer'),
            StringStruct('ProductVersion', '{VERSION[0]}.{VERSION[1]}.{VERSION[2]}'),
            StringStruct('LegalTrademarks', 'WhatsApp is a trademark of Meta Platforms, Inc.'),
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct('Translation', [0x0409, 1200])])
  ]
)
"""

import os
out = os.path.join(os.path.dirname(__file__), "version_info.txt")
with open(out, "w", encoding="utf-8") as f:
    f.write(info)
print(f"version_info.txt generado (v{VERSION[0]}.{VERSION[1]}.{VERSION[2]})")
