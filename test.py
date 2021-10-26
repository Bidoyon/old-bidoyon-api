import requests
import json

# res = requests.post("http://localhost:8000/users", data=json.dumps({"username": "axel", "password": "mineto", "permission": "admin"}))

# res = requests.get("http://localhost:8000/users", data=json.dumps({"username": "axel", "password": "mineto"}))

# res = requests.delete("http://localhost:8000/users", data=json.dumps({"username": "axel"}))

# res = requests.post("http://localhost:8000/pressings", data=json.dumps({}))

# res = requests.post("http://localhost:8000/pressings", data=json.dumps({"number": 2, "added_juice": 45, "added_apples": 20}))

# res = requests.get("http://localhost:8000/pressings")

res = requests.get("http://localhost:8000/tokens", data=json.dumps({"token": "988b7e75d8a3ed3fe2c1fe74eabb82074ec8f19137e907034f6ee15e2639c0a1"}))

print(res.json())
