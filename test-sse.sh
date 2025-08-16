#!/bin/bash

# Test SSE connection to backend
echo "Testing Backend SSE Connection"
echo "==============================="
echo ""
echo "Please provide your Firebase auth token (you can get this from the browser console):"
echo "In the browser console, run: await firebase.auth().currentUser.getIdToken()"
echo ""
read -p "Enter token: " TOKEN

echo ""
echo "Connecting to SSE endpoint..."
echo "Listening for events (press Ctrl+C to stop):"
echo ""

# Connect to SSE endpoint with curl
curl -N -H "Accept: text/event-stream" \
     "http://localhost:8000/api/v1/events/stream?client_id=xyz-corp&event_types=gmail_processed,trade_matched,match_created,duplicate_detected&token=$TOKEN"