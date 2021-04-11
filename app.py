from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from os import getenv, environ
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)

app.secret_key = getenv("SECRET_KEY")


@app.route('/')
def hello_world():
    return redirect("/boards")


@app.route('/register', methods=["GET"])
def register_form():
    return render_template("register.html")


@app.route('/register', methods=["POST"])
def do_register():
    username = request.form["username"]
    password_hash = generate_password_hash(request.form["password"])
    query = "INSERT INTO users (username, password) VALUES (:username, :password) RETURNING id"
    result = db.session.execute(query, {"username": username, "password": password_hash})
    db.session.commit()
    uid = result.fetchall()[0]["id"]
    session["uid"] = uid
    session["username"] = username
    return redirect("/boards")


@app.route('/login', methods=["GET"])
def index():
    return render_template("login.html")


@app.route('/login', methods=["POST"])
def do_login():
    username = request.form["username"]
    password = request.form["password"]
    query = "SELECT id, password FROM users WHERE username = :username"
    result = db.session.execute(query, {"username": username}).fetchall()[0]
    uid = result.id
    pw_hash = result.password
    if check_password_hash(pw_hash, password):
        session["uid"] = uid
        session["username"] = username
        return redirect("/boards")
    else:
        return redirect("/login")


@app.route('/boards', methods=["GET"])
def show_boards():
    if "uid" not in session:
        return redirect("/login")
    board_query = "SELECT b.id, b.name, " \
                  "MAX(m.created_at) as last_comment, " \
                  "COUNT(DISTINCT t.id) as thread_count, " \
                  "COUNT(m.id) as comment_count " \
                  "FROM boards b LEFT JOIN threads t ON t.board_id = b.id " \
                  "LEFT JOIN messages m ON m.thread_id = t.id " \
                  "GROUP BY b.id"
    result = db.session.execute(board_query)
    boards = result.fetchall()
    return render_template("boards.html", boards=boards)


@app.route('/boards', methods=["POST"])
def create_board():
    name = request.form["board_name"]
    query = "INSERT INTO boards (name) VALUES (:name)"
    db.session.execute(query, {"name": name})
    db.session.commit()
    return redirect("/boards")


@app.route('/boards/<int:board_id>', methods=["GET"])
def show_board(board_id):
    board_query = "SELECT id, name FROM boards WHERE id = :board_id"
    result = db.session.execute(board_query, {"board_id": board_id})
    board = result.fetchall()[0]
    thread_query = "SELECT t.id, t.name, t.board_id, " \
                   "MAX(m.created_at) as last_comment, " \
                   "COUNT(m.id) as message_count " \
                   "FROM threads t LEFT JOIN messages m ON m.thread_id = t.id WHERE board_id = :board_id GROUP BY t.id "
    result = db.session.execute(thread_query, {"board_id": board_id})
    threads = result.fetchall()
    return render_template("board.html", board=board, threads=threads)


@app.route('/boards/<int:board_id>/delete', methods=["GET"])
def delete_board(board_id):
    board_query = "DELETE FROM boards WHERE id = :board_id"
    db.session.execute(board_query, {"board_id": board_id})
    db.session.commit()
    return redirect("/boards")


@app.route('/boards/<int:board_id>/threads', methods=["POST"])
def create_thread(board_id):
    name = request.form["name"]
    content = request.form["content"]
    now = datetime.now()
    thread_query = "INSERT INTO threads (name, board_id, created_by) " \
                   "VALUES (:name, :board_id, :created_by) RETURNING id"
    result = db.session.execute(thread_query, {
        "name": name,
        "board_id": board_id,
        "created_by": session["uid"]
    })
    db.session.commit()
    thread_id = result.fetchall()[0]["id"]
    message_query = "INSERT INTO messages (content, thread_id, author_id, created_at) " \
                    "VALUES (:content, :thread_id, :author_id, :created_at) RETURNING id"
    db.session.execute(message_query, {
        "content": content,
        "thread_id": thread_id,
        "author_id": session["uid"],
        "created_at": now
    })
    db.session.commit()
    return redirect("/threads/" + str(thread_id))


@app.route('/threads/<int:thread_id>', methods=["GET"])
def show_thread(thread_id):
    thread_query = "SELECT id, name FROM threads t WHERE id = :thread_id"
    result = db.session.execute(thread_query, {"thread_id": thread_id})
    thread = result.fetchall()[0]
    messages_query = "SELECT m.id, m.content, m.created_at, u.username as author " \
                     "FROM messages m LEFT JOIN users u on m.author_id = u.id " \
                     "WHERE thread_id = :thread_id " \
                     "ORDER BY m.created_at ASC "
    result = db.session.execute(messages_query, {"thread_id": thread_id})
    comments = result.fetchall()
    return render_template("thread.html", thread=thread, messages=comments)


@app.route('/threads/<int:thread_id>', methods=["POST"])
def post_message(thread_id):
    content = request.form["content"]
    now = datetime.now()
    message_query = "INSERT INTO messages (content, thread_id, author_id, created_at) " \
                    "VALUES (:content, :thread_id, :author_id, :created_at) RETURNING id"
    db.session.execute(message_query, {
        "content": content,
        "thread_id": thread_id,
        "author_id": session["uid"],
        "created_at": now
    })
    db.session.commit()
    return redirect("/threads/" + str(thread_id))


@app.route("/logout")
def logout():
    if "username" in session:
        del session["username"]
    if "uid" in session:
        del session["uid"]
    return redirect("/login")


if __name__ == '__main__':
    app.run()
