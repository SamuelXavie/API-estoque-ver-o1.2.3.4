from fastapi import FastAPI
from dotenv import load_dotenv
app = FastAPI()

@app.get("/")
def home():
    return {"msg": "ok"}

print("OK")

