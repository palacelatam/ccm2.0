# Test SSE connection to backend
Write-Host "Testing Backend SSE Connection" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green
Write-Host ""
Write-Host "Please provide your Firebase auth token (you can get this from the browser console):" -ForegroundColor Yellow
Write-Host "In the browser console, run: await firebase.auth().currentUser.getIdToken()" -ForegroundColor Cyan
Write-Host ""
$TOKEN = Read-Host "Enter token"

Write-Host ""
Write-Host "Connecting to SSE endpoint..." -ForegroundColor Yellow
Write-Host "Listening for events (press Ctrl+C to stop):" -ForegroundColor Yellow
Write-Host ""

# Connect to SSE endpoint with curl
$url = "http://localhost:8000/api/v1/events/stream?client_id=xyz-corp&event_types=gmail_processed,trade_matched,match_created,duplicate_detected&token=$TOKEN"
curl.exe -N -H "Accept: text/event-stream" $url