#!/usr/bin/env python3
"""
Test Backend SSE Connection
This script tests the backend SSE (Server-Sent Events) connection directly
"""

import sys
import json
import time
import requests
import sseclient
from typing import Optional

def test_sse_connection(token: Optional[str] = None):
    """Test SSE connection to backend"""
    
    print("=" * 50)
    print("Testing Backend SSE Connection")
    print("=" * 50)
    
    if not token:
        print("\nPlease provide your Firebase auth token.")
        print("You can get this from the browser console by running:")
        print("  await firebase.auth().currentUser.getIdToken()")
        print("")
        token = input("Enter token: ").strip()
    
    # Build SSE URL with parameters
    base_url = "http://localhost:8000/api/v1/events/stream"
    params = {
        "client_id": "xyz-corp",
        "event_types": "gmail_processed,trade_matched,match_created,duplicate_detected",
        "token": token
    }
    
    # Build URL with query parameters
    url = base_url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    print(f"\nConnecting to: {base_url}")
    print("Client ID: xyz-corp")
    print("Event Types: gmail_processed, trade_matched, match_created, duplicate_detected")
    print("\nListening for events (press Ctrl+C to stop)...")
    print("-" * 50)
    
    try:
        # Create SSE client
        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache"
        }
        
        response = requests.get(url, headers=headers, stream=True)
        
        if response.status_code != 200:
            print(f"❌ Connection failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        client = sseclient.SSEClient(response)
        
        print("✅ Connected successfully!")
        print("-" * 50)
        
        # Listen for events
        for event in client.events():
            timestamp = time.strftime("%H:%M:%S")
            
            # Parse event data
            try:
                data = json.loads(event.data)
                event_type = data.get('type', 'unknown')
                
                if event_type == 'connection':
                    print(f"[{timestamp}] 🔗 CONNECTION: {data.get('data', {}).get('status')} - Connection ID: {data.get('data', {}).get('connection_id')}")
                
                elif event_type == 'heartbeat':
                    print(f"[{timestamp}] 💓 HEARTBEAT")
                
                elif event_type == 'event':
                    event_data = data.get('data', {})
                    print(f"[{timestamp}] 📡 EVENT: {event_data.get('type')} - {event_data.get('title')}")
                    print(f"            Message: {event_data.get('message')}")
                    if event_data.get('action'):
                        print(f"            Action: {event_data.get('action')}")
                
                elif event_type == 'error':
                    print(f"[{timestamp}] ❌ ERROR: {data.get('data', {}).get('message')}")
                
                else:
                    print(f"[{timestamp}] 📦 {event_type.upper()}: {json.dumps(data, indent=2)}")
                    
            except json.JSONDecodeError:
                print(f"[{timestamp}] 📄 RAW: {event.data}")
            
    except KeyboardInterrupt:
        print("\n\n✋ Connection closed by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\nTest completed!")

def test_emit_event():
    """Emit a test event to the backend"""
    print("\nEmitting test event...")
    
    url = "http://localhost:8000/api/v1/events/test"
    params = {
        "title": f"SSE Test {time.strftime('%H:%M:%S')}",
        "message": "Testing backend SSE connection",
        "client_id": "xyz-corp"
    }
    
    try:
        response = requests.post(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Event emitted successfully! Event ID: {data.get('event_id')}")
        else:
            print(f"❌ Failed to emit event: {response.status_code}")
    except Exception as e:
        print(f"❌ Error emitting event: {e}")

if __name__ == "__main__":
    # Check if sseclient is installed
    try:
        import sseclient
    except ImportError:
        print("❌ sseclient-py is not installed. Please install it:")
        print("   pip install sseclient-py requests")
        sys.exit(1)
    
    # If token provided as argument, use it
    token = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Test the connection
    test_sse_connection(token)