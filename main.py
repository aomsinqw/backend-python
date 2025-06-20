from fastapi import FastAPI

from routers import file, login


app = FastAPI()

app.include_router(file.router, prefix="/file")
app.include_router(login.router, prefix="/login")