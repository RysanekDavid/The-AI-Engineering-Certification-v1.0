from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent import get_reply

app = FastAPI(title="chat-app")


class ChatRequest(BaseModel):
    message: str
    conversation_id: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def index() -> FileResponse:
    return FileResponse("static/index.html")


@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    reply = await get_reply(request.message, request.conversation_id)
    return ChatResponse(reply=reply)


app.mount("/static", StaticFiles(directory="static"), name="static")
