from db import db


def all():
    board_query = "SELECT b.id, b.name, b.is_secret, " \
                  "MAX(m.created_at) as last_comment, " \
                  "COUNT(DISTINCT t.id) as thread_count, " \
                  "COUNT(m.id) as comment_count " \
                  "FROM boards b " \
                  "LEFT JOIN threads t ON t.board_id = b.id " \
                  "LEFT JOIN messages m ON m.thread_id = t.id " \
                  "GROUP BY b.id"
    result = db.session.execute(board_query)
    return result.fetchall()


def create(board_name, is_secret, secret_board_users):
    query = "INSERT INTO boards (name, is_secret) VALUES (:name, :is_secret) RETURNING id"
    result = db.session.execute(query, {"name": board_name, "is_secret": is_secret})
    db.session.commit()
    board_id = result.fetchall()[0]["id"]
    if is_secret:
        private_board_query = "INSERT INTO private_board_users (board_id, user_id) VALUES (:board_id, :user_id)"
        for user_id in secret_board_users:
            db.session.execute(private_board_query, {"board_id": board_id, "user_id": user_id})
        db.session.commit()


def get(board_id):
    board_query = "SELECT id, name, is_secret FROM boards WHERE id = :board_id"
    result = db.session.execute(board_query, {"board_id": board_id})
    board = result.fetchall()[0]
    thread_query = "SELECT t.id, t.name, t.board_id, " \
                   "MAX(m.created_at) as last_comment, " \
                   "COUNT(m.id) as message_count " \
                   "FROM threads t LEFT JOIN messages m ON m.thread_id = t.id WHERE board_id = :board_id GROUP BY t.id "
    result = db.session.execute(thread_query, {"board_id": board_id})
    threads = result.fetchall()
    return {"id": board.id, "name": board.name, "is_secret": board.is_secret, "threads": threads}


def delete(board_id):
    board_query = "DELETE FROM boards WHERE id = :board_id"
    db.session.execute(board_query, {"board_id": board_id})
    db.session.commit()

