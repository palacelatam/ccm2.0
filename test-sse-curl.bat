@echo off
echo Testing SSE Connection with curl
echo =================================
echo.
echo Connecting to test SSE endpoint (no auth required)...
echo Press Ctrl+C to stop
echo.
curl -N -H "Accept: text/event-stream" http://localhost:8000/api/v1/events/test-stream