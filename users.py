from db import db


def create(username, password_hash):
    query = "INSERT INTO users (username, password) VALUES (:username, :password) RETURNING id"
    result = db.session.execute(query, {"username": username, "password": password_hash})
    db.session.commit()
    uid = result.fetchall()[0]["id"]
    return {"success": True, "uid": uid}


def all():
    users_query = "SELECT id, username FROM users"
    result = db.session.execute(users_query)
    return result.fetchall()