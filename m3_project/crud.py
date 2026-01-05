from fastapi import FastAPI, HTTPException, status, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


app = FastAPI()

# Настройка Jinja2 и статических файлов
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Модель для входных данных (запросов: создание и обновление)
class MessageCreate(BaseModel):
    content: str


# Модель для ответов и хранения в базе данных
class Message(BaseModel):
    id: int
    content: str


# Инициализируем messages_db как список объектов Message
messages_db: list[Message] = [Message(id=0, content="Первое сообщение в FastAPI")]


# GET /messages: Возвращает весь список сообщений
@app.get("/messages", response_model=list[Message])
async def read_messages() -> list[Message]:
    return messages_db


# GET /messages/{message_id}: Получение одного сообщения по ID
@app.get("/messages/{message_id}", response_model=Message)
async def read_message(message_id: int) -> Message:
    for message in messages_db:
        if message.id == message_id:
            return message
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


# POST /messages: Создание нового сообщения
@app.post("/messages", response_model=Message, status_code=status.HTTP_201_CREATED)
async def create_message(message_create: MessageCreate) -> Message:
    # Генерируем новый ID на основе максимального существующего
    next_id = max((msg.id for msg in messages_db), default=-1) + 1
    new_message = Message(id=next_id, content=message_create.content)
    messages_db.append(new_message)
    return new_message


# PUT /messages/{message_id}: Обновление существующего сообщения
@app.put("/messages/{message_id}", response_model=Message)
async def update_message(message_id: int, message_create: MessageCreate) -> Message:
    for i, message in enumerate(messages_db):
        if message.id == message_id:
            updated_message = Message(id=message_id, content=message_create.content)
            messages_db[i] = updated_message
            return updated_message
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


# DELETE /messages/{message_id}: Удаление одного сообщения
@app.delete("/messages/{message_id}", status_code=status.HTTP_200_OK)
async def delete_message(message_id: int) -> dict:
    for i, message in enumerate(messages_db):
        if message.id == message_id:
            messages_db.pop(i)
            return {"detail": f"Message ID={message_id} deleted!"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


# DELETE /messages: Удаление всех сообщений
@app.delete("/messages", status_code=status.HTTP_200_OK)
async def delete_messages() -> dict:
    messages_db.clear()
    return {"detail": "All messages deleted!"}


@app.get("/web/messages", response_class=HTMLResponse)
async def get_messages_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "messages": messages_db})


# Страница создания сообщения
@app.get("/web/messages/create", response_class=HTMLResponse)
async def get_create_message_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


# Обработка формы создания сообщения
@app.post("/web/messages", response_class=HTMLResponse)
async def create_message_form(request: Request, content: str = Form(...)):
    next_id = max((msg.id for msg in messages_db), default=-1) + 1
    new_message = Message(id=next_id, content=content)
    messages_db.append(new_message)
    return templates.TemplateResponse("index.html", {"request": request, "messages": messages_db})


# Страница одного сообщения
@app.get("/web/messages/{message_id}", response_class=HTMLResponse)
async def get_message_detail_page(request: Request, message_id: int):
    for message in messages_db:
        if message.id == message_id:
            return templates.TemplateResponse("detail.html", {"request": request, "message": message})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сообщение не найдено")