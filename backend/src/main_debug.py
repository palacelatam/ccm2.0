"""
Debug version - minimal FastAPI app
"""

from fastapi import FastAPI

app = FastAPI(title="Debug API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_debug:app", host="127.0.0.1", port=8000, reload=True)