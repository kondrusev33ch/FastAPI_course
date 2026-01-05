from typing import Annotated  # позволяет избежать ошибок 
from fastapi import (
    FastAPI, 
    Path,  # для валидации параметров пути, т.е. только для /user/{username}/{age} таких
    Query,  # позволяет задавать правила валидации и метаданные, которые улучшают документацию API в Swagger UI и ReDoc
)

app = FastAPI()


@app.get("/")  # маршрут GET запроса
async def welcome() -> dict:  # асинхронность для большей производительности и обязательно прописываем типы для автоматической генерации документации
    return {"message": "Hello, FastAPI!"}


@app.get("/hello/{user}")
async def welcome_user(user: str) -> dict:
    return {"user": f'Hello {user}'}


@app.get("/hello/{first_name}/{last_name}")
async def welcome_user(first_name: str, last_name: str) -> dict:
    return {"user": f'Hello {first_name} {last_name}'}


@app.get("/order/{order_id}")
async def order(order_id: int) -> dict:
    return {"id": order_id}


# @app.get("/user")
# async def login(username: str, age: int | None = None) -> dict:
#     return {"user": username, "age": age}


@app.get("/employee/{name}/company/{company}")
async def get_employee(name: str, department: str, company: str) -> dict:
    return {"Employee": name, "Company": company, "Department": department}

# Параметры Path и Query
# Метаданные:
#     title: Название параметра для документации.
#     description: Подробное описание параметра.
#     examples: Пример значения параметра.
#     include_in_schema: Логический параметр, определяющий, включать ли параметр в схему OpenAPI (по умолчанию True).

# Правила валидации:
#     min_length: Минимальная длина строки.
#     max_length: Максимальная длина строки.
#     pattern: Регулярное выражение для проверки строки.
#     gt: Значение должно быть больше указанного (для чисел).
#     ge: Значение должно быть больше или равно указанному.
#     lt: Значение должно быть меньше указанного.
#     le: Значение должно быть меньше или равно указанному.


@app.get("/user/{username}/{age}")
async def login(username: str = Path(min_length=3, max_length=15, description='Enter your username', example='Ilya'),
                age: int = Path(ge=0, le=100, description="Enter your age")) -> dict:
    return {"user": username, "age": age}


@app.get("/puser/{username}")
async def login(
        username: Annotated[
            str, Path(min_length=3, max_length=15, description='Enter your username',
                      example='permin0ff')],
        first_name: Annotated[str | None, Query(max_length=10)] = None) -> dict:
    return {"puser": username, "Name": first_name}


@app.get("/luser")
async def search(
    people: Annotated[
        list[str],
        Query(min_length=1, max_length=5, description="List of user names", example=["Tom", "Sam"])  # обработка списка
    ]
) -> dict:
    return {"luser": people}


@app.get("/user/{username}")
async def login(
        username: Annotated[
            str, Path(min_length=3, max_length=15, description='Enter your username',
                      example='permin0ff')],
        first_name: Annotated[
            str | None, Query(max_length=10, pattern="^J|s$")] = None) -> dict:  # pattern для использования re
    return {"user": username, "Name": first_name}


# uvicorn api:app --port 8000 --reload
# В этой команде Uvicorn принимает следующие аргументы:

# api:app - указывает, где находится приложение:
# api - имя файла без расширения .py,
# app - имя переменной, содержащей экземпляр FastAPI.

# --port 8000 - задаёт порт, который будет слушать сервер.

# --reload - включает автоматическую перезагрузку при изменении кода (используется только в режиме разработки).