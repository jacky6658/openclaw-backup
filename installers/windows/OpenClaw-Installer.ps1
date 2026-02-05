<#
OpenClaw Windows Installer (Milestone 1)
- Audience: non-technical users
- Design goal: safe install + verify only (no gateway start, no secrets)

This script is meant to be invoked by a GUI wrapper later (MSI/EXE).
For now it can be run from an elevated PowerShell.
#>

$ErrorActionPreference = 'Stop'

function Write-Step($msg) {
  Write-Host "\n==> $msg" -ForegroundColor Cyan
}

function Abort($msg) {
  Write-Host "\n[ERROR] $msg" -ForegroundColor Red
  exit 1
}

function Test-Command($name) {
  return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

Write-Step "Preflight"
if (-not (Test-Command "node") -or -not (Test-Command "npm")) {
  Write-Host "Node.js / npm not found." -ForegroundColor Yellow
  Write-Host "Please install Node.js LTS first: https://nodejs.org/en/download" -ForegroundColor Yellow
  Abort "Missing Node.js"
}

Write-Step "Install OpenClaw (npm global)"
# Use npm prefix global location
npm install -g openclaw

Write-Step "Verify"
openclaw --version
openclaw status

Write-Step "Done"
Write-Host "OpenClaw installed successfully. Next: openclaw dashboard (optional)." -ForegroundColor Green
