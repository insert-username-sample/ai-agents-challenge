# ===================================================================================
#               CLAUSELY WORKFLOW CONTROL CENTER — USER 5 DEVELOPMENT SPACE
# ===================================================================================
# This script automates development, testing, and Google account profile routing
# to guarantee you are always operating under User Index 5 (/u/5/) for GCP services.
# ===================================================================================

$VENV_PYTHON = "G:\AntiGravity Projects\clausely\clausely-adk\.venv\Scripts\python.exe"
$VENV_STREAMLIT = "G:\AntiGravity Projects\clausely\clausely-adk\.venv\Scripts\streamlit.exe"

Clear-Host
Write-Host "===================================================================================" -ForegroundColor Cyan
Write-Host "          CLAUSELY DEV WORKFLOW - CONFIGURED FOR USER INDEX 5 (/u/5/)              " -ForegroundColor Cyan
Write-Host "===================================================================================" -ForegroundColor Cyan
Write-Host "This workflow automates operations, runs tests, and opens Google profiles safely." -ForegroundColor Gray
Write-Host "-----------------------------------------------------------------------------------" -ForegroundColor Gray

function Show-Menu {
    Write-Host ""
    Write-Host "1. Launch Streamlit Application Frontend" -ForegroundColor Yellow
    Write-Host "2. Launch FastAPI Backend Service" -ForegroundColor Yellow
    Write-Host "3. Run Complete 50-Test Pytest Suite" -ForegroundColor Yellow
    Write-Host "4. Open Google Programmable Search Control Panel (User 5 Profile)" -ForegroundColor Green
    Write-Host "5. Open Google Cloud API Library (Enable Custom Search API)" -ForegroundColor Green
    Write-Host "6. Open Firebase Developer Console (User 5 Profile)" -ForegroundColor Green
    Write-Host "7. Run DeepSearch Litigation Monte Carlo Simulator (1,200 Timelines)" -ForegroundColor Magenta
    Write-Host "8. Exit" -ForegroundColor Red
    Write-Host ""
}

do {
    Show-Menu
    $choice = Read-Host "Select an option [1-8]"
    
    switch ($choice) {
        "1" {
            Write-Host "`nLaunching Streamlit Frontend on http://localhost:8501..." -ForegroundColor Cyan
            Start-Process -FilePath $VENV_STREAMLIT -ArgumentList "run app/streamlit_app.py" -NoNewWindow
        }
        "2" {
            Write-Host "`nLaunching FastAPI Backend on http://localhost:8080..." -ForegroundColor Cyan
            Start-Process -FilePath $VENV_PYTHON -ArgumentList "-m uvicorn app.main:app --reload --port 8080" -NoNewWindow
        }
        "3" {
            Write-Host "`nExecuting full pytest suite (50 tests)..." -ForegroundColor Cyan
            Start-Process -FilePath $VENV_PYTHON -ArgumentList "-m pytest" -Wait
        }
        "4" {
            Write-Host "`nOpening Programmable Search Control Panel under User Index 5..." -ForegroundColor Green
            Start-Process "https://programmablesearchengine.google.com/u/5/controlpanel/all"
        }
        "5" {
            Write-Host "`nOpening GCP API Library to Enable Custom Search API (User 5)..." -ForegroundColor Green
            Start-Process "https://console.cloud.google.com/apis/library/customsearch.googleapis.com?user=5"
        }
        "6" {
            Write-Host "`nOpening Firebase Developer Console under User Index 5..." -ForegroundColor Green
            Start-Process "https://console.firebase.google.com/u/5/"
        }
        "7" {
            Write-Host "`nRunning DeepSearch Litigation Monte Carlo Simulator..." -ForegroundColor Magenta
            Start-Process -FilePath $VENV_PYTHON -ArgumentList "-m scratch.deep_strategist_simulation" -Wait
        }
        "8" {
            Write-Host "`nExiting Workflow Control Center. Have a great session!" -ForegroundColor Gray
            break
        }
        Default {
            Write-Host "`nInvalid choice. Please select a valid number between 1 and 8." -ForegroundColor Red
        }
    }
} while ($true)
