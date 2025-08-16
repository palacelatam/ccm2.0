#!/usr/bin/env python3
"""
Test SSE Connection without Authentication
This creates a mock SSE endpoint to test the connection locally
"""

import asyncio
import json
import time
from aiohttp import web
import threading

# Start a mock SSE server
async def mock_sse_handler(request):
    """Mock SSE endpoint that sends test events"""
    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
        }
    )
    await response.prepare(request)
    
    # Send initial connection message
    await response.write(f"data: {json.dumps({'type': 'connection', 'data': {'status': 'connected', 'connection_id': 'test-123'}})}\n\n".encode('utf-8'))
    
    # Send periodic events
    event_count = 0
    try:
        while True:
            await asyncio.sleep(5)  # Send event every 5 seconds
            
            # Send heartbeat
            if event_count % 2 == 0:
                await response.write(f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time()})}\n\n".encode('utf-8'))
            else:
                # Send test event
                event_data = {
                    'type': 'event',
                    'data': {
                        'id': f'event-{event_count}',
                        'type': 'gmail_processed',
                        'title': f'Test Event {event_count}',
                        'message': f'This is test event number {event_count}',
                        'priority': 'medium',
                        'client_id': 'xyz-corp',
                        'timestamp': time.time()
                    }
                }
                await response.write(f"data: {json.dumps(event_data)}\n\n".encode('utf-8'))
                print(f"[SERVER] Sent event {event_count}")
            
            event_count += 1
            
    except Exception as e:
        print(f"[SERVER] Connection closed: {e}")
    
    return response

async def init_app():
    """Initialize the mock server"""
    app = web.Application()
    app.router.add_get('/test/sse', mock_sse_handler)
    return app

def run_mock_server():
    """Run the mock SSE server"""
    print("\n" + "="*60)
    print("Mock SSE Server for Testing")
    print("="*60)
    print("\nStarting mock SSE server on http://localhost:8888/test/sse")
    print("This server simulates SSE events without authentication")
    print("\nTo test, open another terminal and run:")
    print("  curl -N http://localhost:8888/test/sse")
    print("\nOr update the frontend to connect to this endpoint temporarily")
    print("\nPress Ctrl+C to stop the server")
    print("-"*60 + "\n")
    
    app = asyncio.new_event_loop().run_until_complete(init_app())
    web.run_app(app, host='localhost', port=8888, print=lambda x: None)

if __name__ == "__main__":
    try:
        run_mock_server()
    except KeyboardInterrupt:
        print("\n\n[SERVER] Stopped by user")