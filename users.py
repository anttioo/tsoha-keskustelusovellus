from sqlalchemy import exc
from db import db


def create(username, password_hash):
    query = "INSERT INTO users (username, password, role) VALUES (:username, :password, 'user') RETURNING id"
    try:
        result = db.session.execute(query, {"username": username, "password": password_hash})
        db.session.commit()
        uid = result.fetchall()[0]["id"]
        return {"success": True, "uid": uid}
    except exc.SQLAlchemyError:
        return {"success": False, "uid": None}


def get_all():
    users_query = "SELECT id, username FROM users"
    result = db.session.execute(users_query)
    return result.fetchall()


def get_by_username(username):
    query = "SELECT id, password, role FROM users WHERE username = :username"
    return db.session.execute(query, {"username": username}).fetchone()


def get_private_boards(user_id):
    query = "SELECT board_id FROM private_board_users WHERE user_id = :user_id"
    results = []
    for result in db.session.execute(query, {"user_id": user_id}).fetchall():
        results.append(result["board_id"])
    return results
