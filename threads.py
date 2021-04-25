from db import db
from datetime import datetime


def delete(thread_id):
    message_query = "DELETE FROM threads WHERE id = :thread_id RETURNING board_id"
    result = db.session.execute(message_query, {
        "thread_id": thread_id,
    })
    db.session.commit()
    return result.fetchall()[0]["board_id"]


def rename(thread_id, new_name):
    new_name = new_name
    message_query = "UPDATE threads SET name = :new_name WHERE id = :thread_id"
    db.session.execute(message_query, {
        "new_name": new_name,
        "thread_id": thread_id,
    })
    db.session.commit()


def get(thread_id):
    thread_query = "SELECT id, name, created_by FROM threads t WHERE id = :thread_id"
    result = db.session.execute(thread_query, {"thread_id": thread_id})
    thread = result.fetchall()[0]
    messages_query = "SELECT m.id, m.content, m.created_at, u.username as author " \
                     "FROM messages m LEFT JOIN users u on m.author_id = u.id " \
                     "WHERE thread_id = :thread_id " \
                     "ORDER BY m.created_at ASC "
    result = db.session.execute(messages_query, {"thread_id": thread_id})
    messages = result.fetchall()
    return {"id": thread.id, "name": thread.name, "created_by": thread.created_by, "messages": messages}


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
