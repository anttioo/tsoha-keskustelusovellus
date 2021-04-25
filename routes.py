from flask import redirect, render_template, request, session
from app import app
from db import db
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import users
import messages
import boards


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
    result = users.create(username, password_hash)
    session["uid"] = result["uid"]
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
    return render_template("boards.html", boards=boards.all(), users=users.all())


@app.route('/boards', methods=["POST"])
def create_board():
    is_secret = request.form["is-secret"] is not None
    board_id = boards.create(request.form["board_name"], is_secret, request.form.getlist('secret-board-user'))
    return redirect("/boards/" + str(board_id))


@app.route('/boards/<int:board_id>', methods=["GET"])
def show_board(board_id):
    return render_template("board.html", board=boards.get(board_id))


@app.route('/boards/<int:board_id>/delete', methods=["GET"])
def delete_board(board_id):
    boards.delete(board_id)
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
    thread_query = "SELECT id, name, created_by FROM threads t WHERE id = :thread_id"
    result = db.session.execute(thread_query, {"thread_id": thread_id})
    thread = result.fetchall()[0]
    created_by_me = session["uid"] == thread["created_by"]
    messages_query = "SELECT m.id, m.content, m.created_at, u.username as author " \
                     "FROM messages m LEFT JOIN users u on m.author_id = u.id " \
                     "WHERE thread_id = :thread_id " \
                     "ORDER BY m.created_at ASC "
    result = db.session.execute(messages_query, {"thread_id": thread_id})
    comments = result.fetchall()
    return render_template("thread.html", thread=thread, messages=comments, created_by_me=created_by_me)


@app.route('/threads/<int:thread_id>', methods=["POST"])
def post_message(thread_id):
    messages.create(request.form["content"], thread_id, session["uid"])
    return redirect("/threads/" + str(thread_id))


@app.route('/threads/<int:thread_id>/name', methods=["POST"])
def edit_thread_name(thread_id):
    new_name = request.form["name"]
    message_query = "UPDATE threads SET name = :new_name WHERE id = :thread_id"
    db.session.execute(message_query, {
        "new_name": new_name,
        "thread_id": thread_id,
    })
    db.session.commit()
    return redirect("/threads/" + str(thread_id))


@app.route('/threads/<int:thread_id>/delete', methods=["POST"])
def delete_thread(thread_id):
    message_query = "DELETE FROM threads WHERE id = :thread_id RETURNING board_id"
    result = db.session.execute(message_query, {
        "thread_id": thread_id,
    })
    db.session.commit()
    return redirect("/boards/" + str(result.fetchall()[0]["board_id"]))


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def delete_message(message_id):
    thread_id = messages.delete(message_id)
    return redirect("/threads/" + thread_id)


@app.route('/messages/<int:message_id>/content', methods=["POST"])
def update_message(message_id):
    thread_id = messages.update(message_id, request.form["content"])
    return redirect("/threads/" + str(thread_id))


@app.route('/search', methods=["GET"])
def search():
    search_term = request.args.get("term")
    return render_template("search_results.html", search_term=search_term, messages=messages.search(search_term))


@app.route("/logout")
def logout():
    if "username" in session:
        del session["username"]
    if "uid" in session:
        del session["uid"]
    return redirect("/login")
