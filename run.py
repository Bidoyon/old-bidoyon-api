from uvicorn import run

HOST = "0.0.0.0"
PORT = 8000

if __name__ == "__main__":
    run("app:app", host=HOST, port=PORT)
