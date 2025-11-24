# Path to your repo
$repoRoot = "C:\College notes\Capstone Project\final final final\ai-teaching-assistant-main"

$venvActivate = "$repoRoot\venv\Scripts\Activate.ps1"

# Subdirectories
$backendPath   = "$repoRoot\new-backend"
$budgetPath    = "$repoRoot\BudgetBridge 2\BudgetBridge 3"
$humanoidPath  = "$repoRoot\humanoid\2d mode integ"
# ===============

# 1) Backend: 
Start-Process powershell `
  -WorkingDirectory "$backendPath" `
  -ArgumentList "-NoExit", "-Command", "& '$venvActivate'; uvicorn app:app"

# 2) Frontend:
Start-Process powershell `
  -WorkingDirectory "$budgetPath" `
  -ArgumentList "-NoExit", "-Command", "& '$venvActivate'; npm run dev"

# 3) Humanoid 2D: 
Start-Process powershell `
  -WorkingDirectory "$humanoidPath" `
  -ArgumentList "-NoExit", "-Command", "& '$venvActivate'; npm run dev"
