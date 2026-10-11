# Crear certificado autofirmado para firmar WhatsApp Backup Viewer
# Ejecutar UNA sola vez por equipo: powershell -ExecutionPolicy Bypass -File create_cert.ps1

$existing = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert |
    Where-Object { $_.Subject -like "*WhatsApp Backup Viewer*" }

if ($existing) {
    Write-Host "Ya existe un certificado:" -ForegroundColor Yellow
    $existing | Select-Object Subject, Thumbprint, NotAfter | Format-Table
    Write-Host "Si quieres recrearlo, elimina el existente primero." -ForegroundColor Yellow
    exit 0
}

$cert = New-SelfSignedCertificate `
    -Type CodeSigningCert `
    -Subject "CN=WhatsApp Backup Viewer, O=Duver Marin" `
    -CertStoreLocation Cert:\CurrentUser\My `
    -NotAfter (Get-Date).AddYears(5) `
    -FriendlyName "WhatsApp Backup Viewer Code Signing"

$certBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
$pubCert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2(,$certBytes)

$store = New-Object System.Security.Cryptography.X509Certificates.X509Store("TrustedPublisher", "CurrentUser")
$store.Open("ReadWrite")
$store.Add($pubCert)
$store.Close()

Write-Host ""
Write-Host "Certificado creado exitosamente:" -ForegroundColor Green
$cert | Select-Object Subject, Thumbprint, NotAfter | Format-Table
Write-Host "Valido hasta: $($cert.NotAfter.ToString('dd/MM/yyyy'))" -ForegroundColor Green
Write-Host "El build.bat firmara el .exe automaticamente." -ForegroundColor Green
