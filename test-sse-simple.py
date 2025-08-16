#!/usr/bin/env python3
"""
Simple SSE Test - Emit events and check backend logs
"""

import time
import requests
import threading
import sys

# Fix Unicode output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def emit_test_events():
    """Emit test events periodically"""
    base_url = "http://localhost:8000/api/v1/events/test"
    
    events = [
        {"title": "Test Event 1", "message": "First test event", "client_id": "xyz-corp"},
        {"title": "Gmail Processed", "message": "Email received and processed", "client_id": "xyz-corp"},
        {"title": "Trade Matched", "message": "Trade successfully matched", "client_id": "xyz-corp"},
        {"title": "Duplicate Detected", "message": "Duplicate trade found", "client_id": "xyz-corp"},
    ]
    
    print("=" * 50)
    print("Backend SSE Event Emission Test")
    print("=" * 50)
    print("\nThis will emit test events to the backend.")
    print("Check feedback.md for backend logs to verify event processing.\n")
    
    for i, event_data in enumerate(events, 1):
        print(f"\n[Event {i}/{len(events)}] Emitting: {event_data['title']}")
        
        try:
            response = requests.post(base_url, params=event_data)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  [SUCCESS] Event ID: {data.get('event_id')}")
                print(f"  Check backend logs for broadcasting details")
            else:
                print(f"  [FAILED] HTTP {response.status_code}")
                print(f"  Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"  [ERROR] Connection failed - is the backend running?")
        except Exception as e:
            print(f"  [ERROR] {e}")
        
        if i < len(events):
            print(f"  [WAITING] 3 seconds before next event...")
            time.sleep(3)
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nNext steps:")
    print("1. Check feedback.md for backend logs")
    print("2. Look for 'Broadcasting event' messages")
    print("3. Verify subscription groups count (should be 0 if no frontend)")
    print("4. When ready, run test-backend-sse.py with a token to test SSE connection")

if __name__ == "__main__":
    emit_test_events()