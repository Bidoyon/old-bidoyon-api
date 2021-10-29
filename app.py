from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from sqlite3 import connect

import utils
import models
import csv

app = FastAPI()

database = connect('database.db')
cursor = database.cursor()


def fill_database():

    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, permission INTEGER, token TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS pressings (number INTEGER PRIMARY KEY AUTOINCREMENT, juice INTEGER, apples INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS investments (username TEXT PRIMARY KEY, apples INTEGER)")

    cursor.execute("SELECT * FROM pressings")

    for _ in cursor:

        return

    cursor.execute("INSERT INTO pressings (juice, apples) VALUES (?, ?)", (0, 0))
    cursor.execute("INSERT INTO users (username, password, permission, token) VALUES (?, ?, ?, ?)", ('admin', 'admin', 'admin', utils.token()))


fill_database()


def get_invested_apples():

    apples = 0

    cursor = database.cursor()

    cursor.execute("SELECT apples FROM investments")

    for value in cursor:

        apples += value[0]

    return apples


def get_used_apples():

    apples = 0

    cursor = database.cursor()

    cursor.execute("SELECT apples FROM pressings")

    for value in cursor:

        apples += value[0]

    return apples


def get_produced_juice(pressing=None):

    juice = 0

    cursor = database.cursor()

    if pressing:

        cursor.execute("SELECT juice FROM pressings WHERE number=?", (pressing, ))

    else:

        cursor.execute("SELECT juice FROM pressings")

    for value in cursor:

        juice += value[0]

    return juice


@app.get('/apples')
async def get_apples():

    return JSONResponse({"used": get_used_apples(), "invested": get_invested_apples(), "juice": get_produced_juice()})


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

        cursor.execute("SELECT * FROM investments WHERE username=?", (user.username, ))

        for _ in cursor:

            raise HTTPException(403, "Can't delete an user who's investing apples")

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

    raise HTTPException(404, "Token not found")


@app.get('/pressings')
async def get_pressings():

    cursor = database.cursor()

    cursor.execute("SELECT * FROM pressings")

    pressings = []

    for value in cursor:

        pressings.append((value[0], value[1], value[2], round(value[1]/value[2], 2) if value[1] and value[2] else "Impossible de Calculer "))

    return JSONResponse(pressings, 200)


@app.post('/pressings')
async def add_edit_pressing(pressing: models.NewPressing):

    cursor = database.cursor()

    if pressing.number:

        cursor.execute("SELECT * FROM pressings WHERE number=?", (pressing.number, ))

        for value in cursor:

            cursor = database.cursor()

            if get_used_apples() + pressing.added_apples > get_invested_apples():

                raise HTTPException(422, "Can't use more apple than invested apples")

            if get_used_apples() + pressing.added_apples < 0 or get_produced_juice(pressing.number) + pressing.added_juice < 0:

                raise HTTPException(422, "Can't have a negative number in a pressing")

            data = (value[1] + pressing.added_juice, value[2] + pressing.added_apples, pressing.number)

            cursor.execute("UPDATE pressings SET juice=?, apples=? WHERE number=?", data)

            database.commit()

            cursor.execute("SELECT * FROM pressings WHERE number=?", (pressing.number, ))

            for value in cursor:

                return JSONResponse({"number": value[0], "juice": value[1], "apples": value[2]}, 200)

        raise HTTPException(404, "Pressing not found")

    else:

        if get_used_apples() + pressing.added_apples > get_invested_apples():

            raise HTTPException(422, "Can't use more apple than invested apples")

        if get_used_apples() + pressing.added_apples < 0 or pressing.added_juice < 0:

            raise HTTPException(422, "Can't have a negative number in a pressing")

        data = (pressing.added_juice, pressing.added_apples)

        cursor.execute("INSERT INTO pressings (juice, apples) VALUES (?, ?)", data)

        database.commit()

        return JSONResponse({}, 200)


@app.get('/investments')
async def get_investments(investor: models.Investor):

    if not investor.username:

        cursor.execute("SELECT * FROM investments")

        investments = []

        for value in cursor:

            investments.append((value[0], value[1], round(value[1]/get_invested_apples()*get_produced_juice()) if get_produced_juice() else 0))

        return JSONResponse(investments, 200)

    else:

        cursor.execute("SELECT * FROM investments WHERE username=?", (investor.username, ))

        for value in cursor:

            return JSONResponse({"username": value[0], "apples": value[1], "brings": round(value[1]/get_invested_apples()*get_produced_juice()) if get_produced_juice() else 0}, 200)

        raise HTTPException(404, "Investment not found")


@app.post('/investments')
async def add_edit_investment(investment: models.NewInvestment):

    cursor = database.cursor()

    cursor.execute("SELECT * FROM users WHERE username=?", (investment.username, ))

    for _ in cursor:

        cursor.execute("SELECT * FROM investments WHERE username=?", (investment.username, ))

        for value in cursor:

            if value[1] + investment.apples < 0:

                raise HTTPException(422, "Can't have a negative investment")

            if investment.apples + get_invested_apples() < get_used_apples():

                raise HTTPException(422, "Can't have less invested apples than used apples")

            cursor.execute("UPDATE investments SET apples=? WHERE username=?", (value[1] + investment.apples, investment.username))

            database.commit()

            cursor.execute("SELECT * FROM investments WHERE username=?", (investment.username, ))

            for value in cursor:

                return JSONResponse({"username": value[0], "apples": value[1]}, 200)

        if investment.apples < 0:

            raise HTTPException(422, "Can't have a negative investment")

        if investment.apples + get_invested_apples() < get_used_apples():

            raise HTTPException(422, "Can't have less invested apples than used apples")

        cursor.execute("INSERT INTO investments (username, apples) VALUES (?, ?)", (investment.username, investment.apples))

        database.commit()

        return JSONResponse({}, 200)

    raise HTTPException(404, "User not found")


@app.delete('/investments')
async def delete_investment(investment: models.Investor):

    cursor = database.cursor()

    cursor.execute("SELECT * FROM investments WHERE username=?", (investment.username,))

    for value in cursor:

        if not get_invested_apples() - value[1] < get_used_apples():

            cursor.execute("DELETE FROM investments WHERE username=?", (investment.username, ))

            database.commit()

            return JSONResponse({}, 200)

        else:

            raise HTTPException(403, "Can't have less invested apples than used apples")

    raise HTTPException(404, "Investment not found")


@app.get('/data')
async def send_data():

    cursor = database.cursor()

    cursor.execute("SELECT * FROM investments")

    investments = []

    for value in cursor:

        investments.append((value[0], f'{value[1]}Kg', f'{round(value[1]/get_invested_apples()*get_produced_juice())}L'))

    with open('data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(("Nom", "Pommes"))
        writer.writerows(investments)
        writer.writerow("")
        writer.writerow(("Pommes utilisées :", f'{get_used_apples()}Kg'))
        writer.writerow(("Pommes investies :", f'{get_invested_apples()}Kg'))
        writer.writerow(("Jus produit :", f'{get_produced_juice()}L'))

    return FileResponse(path="data.csv", filename="JusDePomme.csv", media_type='text/csv')
