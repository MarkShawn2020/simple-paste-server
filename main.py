from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import uuid
from typing import Dict, Optional

app = FastAPI(title="Simple Paste Server")

storage: Dict[str, str] = {}

class PasteRequest(BaseModel):
    text: str
    output_format: Optional[str] = "json"

class PasteResponse(BaseModel):
    id: str
    url: str
    plainUrl: str
    jsonUrl: str
    fileUrl: str

class PasteData(BaseModel):
    id: str
    text: str

@app.post("/paste")
async def create_paste(request: Request, paste: PasteRequest):
    if not paste.text:
        raise HTTPException(status_code=400, detail="Text content is required")
    
    paste_id = str(uuid.uuid4())
    storage[paste_id] = paste.text
    
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    url = f"{base_url}/paste/{paste_id}"
    
    response_data = PasteResponse(
        id=paste_id,
        url=url,
        plainUrl=f"{url}?format=plain",
        jsonUrl=f"{url}?format=json",
        fileUrl=f"{url}?format=file"
    )
    
    if paste.output_format == "url":
        return PlainTextResponse(content=url)
    elif paste.output_format == "plain_url":
        return PlainTextResponse(content=f"{url}?format=plain")
    elif paste.output_format == "file_url":
        return PlainTextResponse(content=f"{url}?format=file")
    else:
        return response_data

@app.get("/paste/{paste_id}")
async def get_paste(paste_id: str, format: Optional[str] = "file"):
    if paste_id not in storage:
        raise HTTPException(status_code=404, detail="Paste not found")
    
    text = storage[paste_id]
    
    if format == "json":
        return PasteData(id=paste_id, text=text)
    elif format == "plain":
        return PlainTextResponse(content=text)
    else:
        return Response(
            content=text,
            media_type="text/vtt",
            headers={"Content-Disposition": f"attachment; filename={paste_id}.vtt"}
        )

@app.get("/")
async def root():
    return {
        "message": "Simple Paste Server",
        "usage": {
            "post": "POST /paste with JSON body containing 'text' field and optional 'output_format' (json|url|plain_url|file_url)",
            "get": "GET /paste/{id}?format=file|plain|json (default: file)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)