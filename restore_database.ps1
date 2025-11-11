# PowerShell Script to Restore POWERGRID Face Recognition Database
# Run this script after reinstalling MySQL

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "POWERGRID Database Restoration Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Prompt for MySQL root password
$mysqlPassword = Read-Host "Enter MySQL root password (or press Enter for '!manish!')"
if ([string]::IsNullOrWhiteSpace($mysqlPassword)) {
    $mysqlPassword = "!manish!"
}

Write-Host "`n[1/4] Creating database and tables..." -ForegroundColor Yellow
try {
    mysql -u root -p"$mysqlPassword" < database_schema.sql
    Write-Host "[✅] Database schema created successfully!" -ForegroundColor Green
} catch {
    Write-Host "[❌] Error creating database. Make sure MySQL is installed and password is correct." -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Activate virtual environment
Write-Host "`n[2/4] Activating Python virtual environment..." -ForegroundColor Yellow
if (Test-Path "faceenv\Scripts\Activate.ps1") {
    & "faceenv\Scripts\Activate.ps1"
    Write-Host "[✅] Virtual environment activated!" -ForegroundColor Green
} else {
    Write-Host "[⚠️] Virtual environment not found. Continuing anyway..." -ForegroundColor Yellow
}

# Step 3: Rebuild employee data
Write-Host "`n[3/4] Rebuilding employee face database..." -ForegroundColor Yellow
Write-Host "This may take a few minutes depending on number of employees..." -ForegroundColor Gray
try {
    python employee_encoder_deepface.py
    Write-Host "[✅] Employee database rebuilt!" -ForegroundColor Green
} catch {
    Write-Host "[❌] Error rebuilding employee data." -ForegroundColor Red
    Write-Host "Make sure all dependencies are installed: pip install deepface flask mysql-connector-python numpy scipy opencv-python tqdm" -ForegroundColor Yellow
}

# Step 4: Rebuild event photos data
Write-Host "`n[4/4] Rebuilding event photos database..." -ForegroundColor Yellow
Write-Host "This will take longer - processing all event photos with face detection..." -ForegroundColor Gray
Write-Host "Progress bar will show below..." -ForegroundColor Gray
Write-Host ""
try {
    python main.py
    Write-Host "[✅] Event photos database rebuilt!" -ForegroundColor Green
} catch {
    Write-Host "[❌] Error rebuilding event data." -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Restoration Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create a test user in MySQL (if needed):" -ForegroundColor White
Write-Host "   mysql -u root -p" -ForegroundColor Gray
Write-Host "   USE powergrid_face_db;" -ForegroundColor Gray
Write-Host "   INSERT INTO users (employee_id, password) VALUES ('1001', 'test123');" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start the Flask application:" -ForegroundColor White
Write-Host "   python app.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Open browser: http://127.0.0.1:5000" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

