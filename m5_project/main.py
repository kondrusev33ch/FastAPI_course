from fastapi import FastAPI, Depends, Query, HTTPException
from pydantic import BaseModel
from starlette import status

app = FastAPI()


class Post(BaseModel):
    id: int
    text: str


db = []


async def get_post_or_404(id: int):
    try:
        return db[id]
    except IndexError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.get("/message/{id}")
async def get_message(post: Post = Depends(get_post_or_404)):
    return post


@app.post("/message", status_code=status.HTTP_201_CREATED)
async def create_message(post: Post) -> str:
    post.id = len(db)
    db.append(post)
    return f"Message created!"