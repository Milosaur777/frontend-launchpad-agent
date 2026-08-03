@echo off
:: Wrapper to run the PowerShell script easily from anywhere
:: Usage: oc-profiles [switch|save|list|current] [profile_name]
pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0oc-profiles.ps1" %*
