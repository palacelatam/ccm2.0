"""
Minimal FastAPI app to test schema generation
"""

from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel

app = FastAPI(title="Test API")

class SimpleResponse(BaseModel):
    message: str
    timestamp: datetime

@app.get("/test", response_model=SimpleResponse)
async def test():
    return SimpleResponse(
        message="test",
        timestamp=datetime.now()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_minimal:app", host="127.0.0.1", port=8001, reload=True)