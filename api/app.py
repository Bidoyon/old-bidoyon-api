from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlite3 import connect

import utils
import models

app = FastAPI()

database = connect('database.db')
cursor = database.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, permission INTEGER, token TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS pressings (number INTEGER PRIMARY KEY AUTOINCREMENT, juice INTEGER, apples INTEGER)")


@app.get('/users')
async def get_user(user: models.User):

    cursor = database.cursor()

    data = (user.username, user.password)

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", data)

    for value in cursor:

        token = utils.token()

        cursor.execute("UPDATE users SET token=? WHERE username=?", (token, user.username))

        database.commit()

        return JSONResponse({"username": value[0], "password": value[1], "permission": value[2], "token": token}, 200)

    raise HTTPException(403, "User not found")


@app.post('/users')
async def add_user(user: models.NewUser):

    cursor = database.cursor()

    cursor.execute("SELECT * FROM users WHERE username=?", (user.username, ))

    for _ in cursor:

        raise HTTPException(403, "Already exists")

    token = utils.token()

    data = (user.username, user.password, user.permission, token)

    cursor.execute("INSERT INTO users (username, password, permission, token) VALUES (?, ?, ?, ?)", data)

    database.commit()

    return JSONResponse({"username": data[0], "password": data[1], "permission": data[2], "token": data[3]}, 200)


@app.delete('/users')
async def delete_user(user: models.OldUser):

    cursor = database.cursor()

    cursor.execute("SELECT * FROM users WHERE username=?", (user.username, ))

    for _ in cursor:

        cursor.execute("DELETE FROM users WHERE username=?", (user.username, ))

        database.commit()

        return JSONResponse({"username": user.username}, 200)

    raise HTTPException(404, "User not found")


@app.get('/tokens')
async def get_user_by_token(token: models.Token):

    cursor = database.cursor()

    cursor.execute("SELECT * FROM users WHERE token=?", (token.token, ))

    for value in cursor:

        return JSONResponse({"username": value[0], "permission": value[2]}, 200)

    return HTTPException(404, "Token not found")


@app.get('/pressings')
async def get_pressings():

    cursor = database.cursor()

    cursor.execute("SELECT * FROM pressings")

    pressings = []

    for value in cursor:

        pressings.append((value[0], value[1], value[2], value[1]/value[2] if value[1] and value[2] else "Impossible de Calculer "))

    return JSONResponse(pressings, 200)


@app.post('/pressings')
async def add_edit_pressing(pressing: models.NewPressing):

    cursor = database.cursor()

    if pressing.number:

        cursor.execute("SELECT * FROM pressings WHERE number=?", (pressing.number, ))

        for value in cursor:

            cursor = database.cursor()

            cursor.execute("UPDATE pressings SET juice=?, apples=? WHERE number=?", (value[1] + pressing.added_juice, value[2] + pressing.added_apples, pressing.number))

            database.commit()

            cursor.execute("SELECT * FROM pressings WHERE number=?", (pressing.number, ))

            for value in cursor:

                return JSONResponse({"number": value[0], "juice": value[1], "apples": value[2]}, 200)

        return HTTPException(404, "Pressing not found")

    else:

        cursor.execute("INSERT INTO pressings (juice, apples) VALUES (?, ?)", (pressing.added_juice, pressing.added_apples))

        database.commit()

        return JSONResponse({}, 200)
