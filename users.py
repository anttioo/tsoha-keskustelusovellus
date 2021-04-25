from db import db


def create(username, password_hash):
    query = "INSERT INTO users (username, password) VALUES (:username, :password) RETURNING id"
    result = db.session.execute(query, {"username": username, "password": password_hash})
    db.session.commit()
    uid = result.fetchall()[0]["id"]
    return {"success": True, "uid": uid}


def get_all():
    users_query = "SELECT id, username FROM users"
    result = db.session.execute(users_query)
    return result.fetchall()


def get_by_username(username):
    query = "SELECT id, password FROM users WHERE username = :username"
    return db.session.execute(query, {"username": username}).fetchall()[0]