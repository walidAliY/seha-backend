from fastapi import FastAPI

app = FastAPI()

@app.get("/hey")
def hey():
    return "hello world from seha-backend"