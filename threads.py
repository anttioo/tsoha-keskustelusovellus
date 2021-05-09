from db import db
from datetime import datetime


def delete(thread_id):
    message_query = "DELETE FROM threads WHERE id = :thread_id RETURNING board_id"
    result = db.session.execute(message_query, {
        "thread_id": thread_id,
    })
    db.session.commit()
    row = result.fetchaone()
    if row is None:
        return None
    return row["board_id"]


def rename(thread_id, new_name):
    new_name = new_name
    message_query = "UPDATE threads SET name = :new_name WHERE id = :thread_id"
    db.session.execute(message_query, {
        "new_name": new_name,
        "thread_id": thread_id,
    })
    db.session.commit()


def get(thread_id):
    thread_query = "SELECT t.id, t.name, t.board_id ,t.created_by, b.is_secret " \
                   "FROM threads t " \
                   "LEFT JOIN boards b ON b.id = t.board_id " \
                   "WHERE t.id = :thread_id"
    result = db.session.execute(thread_query, {"thread_id": thread_id})
    thread = result.fetchone()
    if thread is None:
        return None
    messages_query = "SELECT m.id, m.content, m.created_at, u.id as author_id, u.username as author " \
                     "FROM messages m LEFT JOIN users u on m.author_id = u.id " \
                     "WHERE thread_id = :thread_id " \
                     "ORDER BY m.created_at ASC "
    result = db.session.execute(messages_query, {"thread_id": thread_id})
    messages = result.fetchall()
    return {
        "id": thread.id,
        "board_id": thread["board_id"],
        "name": thread.name,
        "created_by": thread.created_by,
        "is_secret_board": thread["is_secret"],
        "messages": messages
    }


def create(thread_name, message_content, board_id, created_by):
    now = datetime.now()
    thread_query = "INSERT INTO threads (name, board_id, created_by) " \
                   "VALUES (:name, :board_id, :created_by) RETURNING id"
    result = db.session.execute(thread_query, {
        "name": thread_name,
        "board_id": board_id,
        "created_by": created_by
    })
    db.session.commit()
    thread_id = result.fetchall()[0]["id"]
    message_query = "INSERT INTO messages (content, thread_id, author_id, created_at) " \
                    "VALUES (:content, :thread_id, :author_id, :created_at) RETURNING id"
    db.session.execute(message_query, {
        "content": message_content,
        "thread_id": thread_id,
        "author_id": created_by,
        "created_at": now
    })
    db.session.commit()
    return thread_id


def get_author_id(thread_id):
    query = "SELECT created_by FROM threads WHERE id = :thread_id"
    result = db.session.execute(query, {"thread_id": thread_id})
    try:
        return result.fetchone()["created_by"]
    except:
        return None
