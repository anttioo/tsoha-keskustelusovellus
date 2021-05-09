from flask import redirect, render_template, request, session
from app import app
from werkzeug.security import check_password_hash, generate_password_hash
import os
import users
import messages
import boards
import threads


def is_admin():
    return session["role"] == "admin"


def is_logged_in():
    return "uid" in session


def user_id():
    return session["uid"]


@app.route('/')
def hello_world():
    return redirect("/boards")


@app.route('/register', methods=["GET"])
def register_form():
    invalid_arg = request.args.get("invalid")
    is_invalid = invalid_arg is not None
    error_message = ""
    if invalid_arg == "unique":
        error_message = "Käyttäjätunnus ei ole uniikki"
    if invalid_arg == "empty":
        error_message = "Käyttäjätunnus tai salasana eivät saa olla tyhjiä"
    return render_template("register.html", is_invalid=is_invalid, error_message=error_message)


@app.route('/register', methods=["POST"])
def do_register():
    username = request.form["username"]
    password = request.form["password"]
    if username == "" or password == "":
        return redirect("/register?invalid=empty")
    result = users.create(username, generate_password_hash(password))
    if result["success"]:
        session["uid"] = result["uid"]
        session["username"] = username
        session["role"] = "user"
        return redirect("/boards")
    else:
        return redirect("/register?invalid=unique")


@app.route('/login', methods=["GET"])
def login():
    invalid = request.args.get("invalid") is not None
    return render_template("login.html", invalid=invalid)


@app.route('/login', methods=["POST"])
def do_login():
    username = request.form["username"]
    user = users.get_by_username(username)
    if user is not None and check_password_hash(user.password, request.form["password"]):
        uid = user.id
        session["uid"] = uid
        session["username"] = username
        session["role"] = user["role"]
        return redirect("/boards")
    else:
        return redirect("/login?invalid=true")


@app.route('/boards', methods=["GET"])
def show_boards():
    if not is_logged_in():
        return redirect("/login")
    boards_list = boards.get_all()
    user_private_boards = users.get_private_boards(user_id())
    return render_template(
        "boards.html",
        boards=boards_list,
        users=users.get_all(),
        user_private_boards=user_private_boards
    )


@app.route('/boards', methods=["POST"])
def create_board():
    if not is_logged_in():
        redirect("/boards")
    board_id = boards.create(
        request.form["board_name"],
        "is-secret" in request.form and is_admin(),
        request.form.getlist('secret-board-user'))
    return redirect("/boards/" + str(board_id))


@app.route('/boards/<int:board_id>', methods=["GET"])
def show_board(board_id):
    if not is_logged_in():
        return redirect("/login")
    board = boards.get(board_id)
    if board is None:
        return render_template("board_404.html"), 404
    if board["is_secret"] and board["id"] not in users.get_private_boards(user_id()) and not is_admin():
        return render_template("board_401.html")
    return render_template("board.html", board=board)


@app.route('/boards/<int:board_id>/delete', methods=["GET"])
def delete_board(board_id):
    if not is_admin():
        return redirect("/boards")
    boards.delete(board_id)
    return redirect("/boards")


@app.route('/boards/<int:board_id>/threads', methods=["POST"])
def create_thread(board_id):
    name = request.form["name"]
    content = request.form["content"]
    if not is_logged_in():
        return redirect("/login")
    if name == "" or content == "":
        redirect("/boards/" + str(board_id))
    thread_id = threads.create(name, content, board_id, session["uid"])
    return redirect("/threads/" + str(thread_id))


@app.route('/threads/<int:thread_id>', methods=["GET"])
def show_thread(thread_id):
    if not is_logged_in():
        return redirect("/login")
    thread = threads.get(thread_id)
    if thread is None:
        return render_template("thread_404.html"), 404
    if not is_admin() and thread["is_secret_board"] and thread["board_id"] not in users.get_private_boards(user_id()):
        return redirect("/boards")
    created_by_me = session["uid"] == thread["created_by"]
    return render_template("thread.html", thread=thread, created_by_me=created_by_me)


@app.route('/threads/<int:thread_id>', methods=["POST"])
def post_message(thread_id):
    content = request.form["content"]
    if not is_logged_in():
        return redirect("/login")
    if content != "":
        messages.create(content, thread_id, session["uid"])
    return redirect("/threads/" + str(thread_id))


@app.route('/threads/<int:thread_id>/name', methods=["POST"])
def edit_thread_name(thread_id):
    new_name = request.form["name"]
    if not is_admin() and threads.get_author_id(thread_id) is not user_id():
        return redirect("/boards/")
    if new_name != "":
        threads.rename(thread_id, new_name)
    return redirect("/threads/" + str(thread_id))


@app.route('/threads/<int:thread_id>/delete', methods=["POST"])
def delete_thread(thread_id):
    if not is_admin() and threads.get_author_id(thread_id) is not user_id():
        return redirect("/boards/")
    board_id = threads.delete(thread_id)
    if board_id is None:
        return render_template("thread_404.html"), 404
    return redirect("/boards/" + str(board_id))


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def delete_message(message_id):
    if not is_admin() and messages.get_author_id(message_id) is not user_id():
        return redirect("/boards/")
    thread_id = messages.delete(message_id)
    if thread_id is None:
        return render_template("thread_404.html"), 404
    return redirect("/threads/" + str(thread_id))


@app.route('/messages/<int:message_id>/content', methods=["POST"])
def update_message(message_id):
    if not is_admin() and messages.get_author_id(message_id) is not user_id():
        return redirect("/boards/")
    thread_id = messages.update(message_id, request.form["content"])
    if thread_id is None:
        return render_template("message_404.html"), 404
    return redirect("/threads/" + str(thread_id))


@app.route('/search', methods=["GET"])
def search():
    if not is_logged_in():
        return redirect("/login")
    search_term = request.args.get("term")
    return render_template(
        "search_results.html",
        search_term=search_term,
        messages=messages.search(search_term, user_id())
    )


@app.route("/logout")
def logout():
    if "username" in session:
        del session["username"]
    if "uid" in session:
        del session["uid"]
    return redirect("/login")


@app.before_request
def check_csrf():
    if "csrf_token" not in session:
        session["csrf_token"] = os.urandom(16).hex()
    if request.method == "POST" and ("csrf_token" not in request.form or
                                     session["csrf_token"] != request.form["csrf_token"]):
        return "invalid csrf token", 403
