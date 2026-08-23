"""CodeGenesis 后端入口"""

from fastapi import FastAPI

app = FastAPI(title="CodeGenesis")


@app.get("/")
def root():
    return {"message": "Hello, CodeGenesis!"}

@app.post("/hello")
def create_hello(name: str):
    return {"message": f"Hello, {name}!"}
