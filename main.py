from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import uuid
from typing import Dict, Optional

app = FastAPI(title="Simple Paste Server")

storage: Dict[str, str] = {}

class PasteRequest(BaseModel):
    text: str

class PasteResponse(BaseModel):
    id: str
    url: str
    plainUrl: str
    jsonUrl: str

class PasteData(BaseModel):
    id: str
    text: str

@app.post("/paste", response_model=PasteResponse)
async def create_paste(request: Request, paste: PasteRequest):
    if not paste.text:
        raise HTTPException(status_code=400, detail="Text content is required")
    
    paste_id = str(uuid.uuid4())
    storage[paste_id] = paste.text
    
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    url = f"{base_url}/paste/{paste_id}"
    
    return PasteResponse(
        id=paste_id,
        url=url,
        plainUrl=f"{url}?format=plain",
        jsonUrl=f"{url}?format=json"
    )

@app.get("/paste/{paste_id}")
async def get_paste(paste_id: str, format: Optional[str] = "plain"):
    if paste_id not in storage:
        raise HTTPException(status_code=404, detail="Paste not found")
    
    text = storage[paste_id]
    
    if format == "plain":
        return PlainTextResponse(content=text)
    else:
        return PasteData(id=paste_id, text=text)

@app.get("/")
async def root():
    return {
        "message": "Simple Paste Server",
        "usage": {
            "post": "POST /paste with JSON body containing 'text' field",
            "get": "GET /paste/{id}?format=json|plain"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)