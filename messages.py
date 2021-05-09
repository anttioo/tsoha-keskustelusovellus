from db import db
from datetime import datetime


def search(search_term):
    search_query = "SELECT m.id as message_id, m.content as content, m.created_at as created_at, " \
                   "t.id as thread_id, t.name as thread_name, b.name as board_name, b.id as board_id, " \
                   "u.username as author " \
                   "FROM messages m " \
                   "LEFT JOIN users u ON m.author_id = u.id " \
                   "LEFT JOIN threads t on t.id = m.thread_id " \
                   "LEFT JOIN boards b on t.board_id = b.id " \
                   "WHERE content LIKE :search_term"
    result = db.session.execute(search_query, {"search_term": "%" + search_term + "%"})
    return result.fetchall()


def update(message_id, new_content):
    message_query = "UPDATE messages SET content = :new_content WHERE id = :message_id RETURNING thread_id"
    result = db.session.execute(message_query, {
        "message_id": message_id,
        "new_content": new_content
    })
    db.session.commit()
    row = result.fetchone()
    if row is None:
        return None
    return row["thread_id"]


def delete(message_id):
    message_query = "DELETE FROM messages WHERE id = :message_id RETURNING thread_id"
    result = db.session.execute(message_query, {
        "message_id": message_id,
    })
    db.session.commit()
    row = result.fetchone()
    if row is None:
        return None
    return row["thread_id"]


def create(content, thread_id, author_id):
    now = datetime.now()
    message_query = "INSERT INTO messages (content, thread_id, author_id, created_at) " \
                    "VALUES (:content, :thread_id, :author_id, :created_at) RETURNING id"
    result = db.session.execute(message_query, {
        "content": content,
        "thread_id": thread_id,
        "author_id": author_id,
        "created_at": now
    })
    db.session.commit()
    return result.fetchall()[0]["id"]


def get_author_id(message_id):
    query = "SELECT author_id FROM messages WHERE id = :message_id"
    result = db.session.execute(query, {"message_id": message_id})
    try:
        return result.fetchone()["author_id"]
    except:
        return None
