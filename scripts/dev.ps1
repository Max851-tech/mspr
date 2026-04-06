param(
  [string]$HostAddr = "0.0.0.0",
  [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path ".\\.env")) {
  Write-Host "Aucun .env détecté. Copie de .env.example -> .env"
  Copy-Item ".\\.env.example" ".\\.env"
}

if (-not (Test-Path ".\\venv")) {
  Write-Host "Création venv"
  py -3.11 -m venv venv
}

Write-Host "Activation venv"
. .\\venv\\Scripts\\Activate.ps1

Write-Host "Installation dépendances"
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Migration BDD (alembic upgrade head)"
$env:DATABASE_URL = (Select-String -Path ".\\.env" -Pattern "^DATABASE_URL=" | ForEach-Object { $_.Line -replace "^DATABASE_URL=", "" })

if (-not $env:DATABASE_URL) {
  throw "DATABASE_URL manquant. Mets-le dans .env (voir .env.example)."
}

if ($env:DATABASE_URL -match "root:password@localhost") {
  Write-Warning "DATABASE_URL est encore sur la valeur par défaut (root:password). Édite .env avec tes identifiants MySQL avant de continuer."
  throw "Identifiants MySQL non configurés."
}

try {
  alembic upgrade head
} catch {
  Write-Error "Impossible d'appliquer les migrations. Vérifie que MySQL tourne et que DATABASE_URL est correct dans .env."
  throw
}

Write-Host "Démarrage API"
uvicorn app.main:app --reload --host $HostAddr --port $Port --env-file .\\.env
