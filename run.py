from uvicorn import run
from app import app

HOST = "localhost"
PORT = 8000

if __name__ == "__main__":
    run(app, host=HOST, port=PORT)
